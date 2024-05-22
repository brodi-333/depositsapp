from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .routers import frontend, users, routes
from .core.security import auth_header_or_session
from .core.config import settings
from .core.exception_handlers import register_exception_handlers


app = FastAPI(docs_url=routes.API_DOCS)
register_exception_handlers(app)
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(frontend.router)
app.include_router(users.router)


@app.get("/secured/")
async def secured(token: Annotated[str, Depends(auth_header_or_session)]) -> dict:
    return {"q": "123"}
