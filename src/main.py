from contextlib import asynccontextmanager

from fastapi import FastAPI, responses
from fastapi.middleware.cors import CORSMiddleware
from src.configurations.database import create_db_and_tables, global_init
# from src.routers import v1_router  # Comment out this old router
from src.api.v1.resources import books
from src.api.v1.resources import sellers
from src.models.base import BaseModel
from src.models.books import Book


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run at startup."""
    # Create tables if not exists
    # await init_models()

    global_init()
    await create_db_and_tables()
    yield

    # Clean-up
    # Do not delete data on shutdown
    # await delete_all_tables()


# Само приложение fastApi. именно оно запускается сервером и служит точкой входа
# в нем можно указать разные параметры для сваггера и для ручек (эндпоинтов).
app = FastAPI(
    title="Book Library App",
    description="Учебное приложение для MTS Shad",
    version="0.0.1",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/openapi.json",
    default_response_class=responses.JSONResponse,
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(v1_router)  # Comment out this old router
app.include_router(books.router, prefix="/api/v1")
app.include_router(sellers.router, prefix="/api/v1")
