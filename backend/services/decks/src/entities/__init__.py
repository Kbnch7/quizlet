from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from .deck import Deck
from .card import Card
from .test_result import TestResult
from .card_result import CardResult
from .category import Category, deck_categories
from .tag import Tag, deck_tags
from .user_card_stats import UserCardStats
from .learn_session import LearnSession
from .deck_stats import DeckStats

__all__ = [
    "Base",
    "Deck",
    "Card",
    "TestResult",
    "CardResult",
    "Category",
    "Tag",
    "UserCardStats",
    "LearnSession",
    "DeckStats",
    "deck_categories",
    "deck_tags",
]
