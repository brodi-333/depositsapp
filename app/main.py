from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import frontend
from app.routers import users


app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(frontend.router)
app.include_router(users.router)
