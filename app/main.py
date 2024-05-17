from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.routers import frontend, users
from app.core.security import auth_header_or_session
from app.core.config import settings


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(frontend.router)
app.include_router(users.router)


@app.get("/secured/")
async def secured(token: Annotated[str, Depends(auth_header_or_session)]) -> dict:
    return {"q": "123"}
