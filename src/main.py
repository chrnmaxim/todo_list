"""Модуль конфигурации FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src import api_constants
from src.config import api_settings
from src.tasks.router import tasks_router

app = FastAPI(
    title=api_settings.APP_NAME, swagger_ui_parameters={"operationsSorter": "method"}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=api_constants.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=api_constants.CORS_METHODS,
)

app.include_router(tasks_router, prefix="/api/v1")


@app.get(
    "/",
    response_class=HTMLResponse,
)
def home():
    return f"""
    <html>
    <head><title>{api_settings.APP_NAME}</title></head>
    <body>
    <h1>{api_settings.APP_NAME} в режиме {api_settings.MODE}</h1>
    <ul>
    <li><a href="/docs">Документация Swagger</a></li>
    <li><a href="/redoc">Документация ReDoc</a></li>
    </ul>
    </body>
    </html>
    """
