from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from . import Base

deck_tags = Table(
    'deck_tags',
    Base.metadata,
    Column('deck_id', Integer, ForeignKey('decks.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, unique=True)

    decks = relationship("Deck", secondary=deck_tags, back_populates="tags", lazy="selectin")
