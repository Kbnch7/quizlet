from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from passlib.context import CryptContext

from . import routes
from .database_client import Base, engine
from .schemas.errors_schemas import CustomError


def to_status_name(status_code: int) -> str:
    return f"{status_code}_{HTTPStatus(status_code).phrase.replace(' ', '_').upper()}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="User service", version="1.0.0", lifespan=lifespan, docs_url="/api/docs"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes.router, prefix="/api")


@app.exception_handler(HTTPException)
async def custom_exception(request: Request, exc: HTTPException):
    if isinstance(exc.detail, str):
        code = exc.detail
    else:
        code = "HTTP_ERROR"

    error = CustomError(
        code=code,
        statusCode=to_status_name(exc.status_code),
    )
    return JSONResponse(status_code=exc.status_code, content=error.model_dump())


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
