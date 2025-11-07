from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from .deck import Deck
from .card import Card
from .test_result import TestResult
from .test_result_card import TestResultCard
from .category import Category
from .tag import Tag

__all__ = ["Base", "Deck", "Card", "TestResult", "TestResultCard", "Category", "Tag"]
