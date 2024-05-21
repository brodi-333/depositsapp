from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas import user_schema, token_schema
from ..core import security, security_user_provider, config
from . import routes

router = APIRouter()


@router.post(routes.API_USER_REGISTER)
async def user_register(registered_user: Annotated[user_schema.UserRegister, Body(examples=[
    {
        "full_name": "string",
        "email": "user@example.com",
        "password": "String1",
        "confirm_password": "String1",
        "agreement": True
    },
])]) -> user_schema.UserOut:
    user_in_db = user_schema.UserInDb(
        **registered_user.model_dump(),
        id=registered_user.email,
        hashed_password=security.get_password_hash(registered_user.password),
    )

    user_encoded = jsonable_encoder(user_in_db)
    security_user_provider.users[user_in_db.id] = user_encoded

    user_out = user_schema.UserOut(**user_in_db.model_dump())

    return user_out


@router.get(routes.API_USER_LIST, response_model=list[user_schema.UserOut])
async def get_users():
    return list(security_user_provider.get_users().values())


@router.post(routes.API_TOKEN)
async def get_access_token(
        request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> token_schema.Token:
    user_in_db = security.authenticate_user(form_data.username, form_data.password)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.settings.SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user_in_db.email}, expires_delta=access_token_expires
    )
    request.session["jwt_token"] = access_token
    return token_schema.Token(access_token=access_token, token_type="bearer")
