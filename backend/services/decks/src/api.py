from fastapi import FastAPI

from .deck.controller import router as deck_router
from .card.controller import router as card_router
from .category.controller import router as category_router
from .test_result.controller import router as result_router


def register_routes(app: FastAPI) -> None:
    app.include_router(deck_router)
    app.include_router(card_router)
    app.include_router(category_router)
    app.include_router(result_router)


