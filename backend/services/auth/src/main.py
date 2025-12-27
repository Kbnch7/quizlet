from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import routes
from .infra.redis_client import redis_manager
from .schemas.errors_schemas import CustomError


def to_status_name(status_code: int) -> str:
    return f"{status_code}_{HTTPStatus(status_code).phrase.replace(' ', '_').upper()}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # async with engine.begin() as conn:
    # await conn.run_sync(Base.metadata.create_all)
    await redis_manager.init_redis()
    yield
    # await engine.dispose()
    await redis_manager.close_redis()


app = FastAPI(
    title="Auth service", version="1.0.0", lifespan=lifespan, docs_url="/api/docs"
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
    detail = None
    if isinstance(exc.detail, str):
        code = exc.detail
    else:
        detail = exc.detail
        code = "HTTP_ERROR"

    error = CustomError(
        code=code, statusCode=to_status_name(exc.status_code), detail=detail
    )
    return JSONResponse(status_code=exc.status_code, content=error.model_dump())
