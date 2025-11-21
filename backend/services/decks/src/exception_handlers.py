from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.exceptions import CategoryNotFoundError, CategoryAlreadyExistsError


async def category_not_found_handler(
    request: Request, exc: CategoryNotFoundError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Unknown categories", "slugs": exc.missing_slugs},
    )


async def category_already_exists_handler(
    request: Request, exc: CategoryAlreadyExistsError
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": f"Category with {exc.field} '{exc.value}' already exists",
            "field": exc.field,
            "value": exc.value,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        CategoryNotFoundError, category_not_found_handler
    )
    app.add_exception_handler(
        CategoryAlreadyExistsError, category_already_exists_handler
    )
