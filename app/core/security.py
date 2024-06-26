from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from . import security_user_provider, config

from ..schemas import user_schema, token_schema
from ..routers import routes


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=routes.API_TOKEN)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def extract_header_token(request: Request) -> str | None:
    try:
        return await oauth2_scheme(request)
    except HTTPException:
        return None


def extract_session_token(request: Request) -> str | None:
    return request.session.get("jwt_token")


def auth_header_or_session(
    header_token: Annotated[str, Depends(extract_header_token)],
    session_token: Annotated[str, Depends(extract_session_token)],
) -> str | None:
    if header_token:
        return header_token
    if session_token:
        return session_token
    raise credentials_exception


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.settings.SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=config.settings.SECURITY_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(auth_header_or_session)]) -> user_schema.UserInDb:
    try:
        payload = jwt.decode(token, config.settings.SECRET_KEY, algorithms=[config.settings.SECURITY_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = token_schema.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = security_user_provider.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[user_schema.UserInDb, Depends(get_current_user)],
) -> user_schema.UserInDb:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def authenticate_user(username: str, password: str) -> user_schema.UserInDb | bool:
    user_in_db = security_user_provider.get_user(username)
    if not user_in_db:
        return False
    if not verify_password(password, user_in_db.hashed_password):
        return False
    return user_in_db
