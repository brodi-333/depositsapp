from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from ..core.config import settings

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "settings": settings,
    })


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "settings": settings,
    })


@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request,
        "settings": settings,
    })


@router.get('/favicon.ico', include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse("app/static/favicon.ico")