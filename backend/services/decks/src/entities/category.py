from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from . import Base

deck_categories = Table(
    'deck_categories',
    Base.metadata,
    Column('deck_id', Integer, ForeignKey('decks.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, unique=True)

    decks = relationship("Deck", secondary=deck_categories, back_populates="categories", lazy="selectin")
