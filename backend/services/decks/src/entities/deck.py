from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship

from . import Base
from .category import deck_categories
from .tag import deck_tags


class Deck(Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, nullable=False)
    cards_amount = Column(Integer, default=0, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    cards = relationship(
        "Card",
        order_by="Card.order_index",
        back_populates="deck",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    categories = relationship(
        "Category",
        secondary=deck_categories,
        back_populates="decks",
        lazy="selectin",
    )
    tags = relationship(
        "Tag", secondary=deck_tags, back_populates="decks", lazy="selectin"
    )
