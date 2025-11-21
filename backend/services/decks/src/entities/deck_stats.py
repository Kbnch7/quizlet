from sqlalchemy import Column, Integer, Float, JSON, ForeignKey
from . import Base


class DeckStats(Base):
    __tablename__ = "deck_statistics"

    deck_id = Column(
        Integer, ForeignKey("decks.id", ondelete="CASCADE"), primary_key=True
    )
    total_tests = Column(Integer, default=0, nullable=False)
    avg_score = Column(Float, default=0.0, nullable=False)
    correct_rate = Column(Float, default=0.0, nullable=False)
    avg_time_seconds = Column(Integer, default=0, nullable=False)
    card_stats = Column(JSON, nullable=True)
