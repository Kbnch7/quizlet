from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from . import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deck_id = Column(
        Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False
    )
    front_text = Column(Text, nullable=False)
    front_image_url = Column(String, nullable=True)
    back_text = Column(Text, nullable=False)
    back_image_url = Column(String, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deck = relationship("Deck", back_populates="cards")
