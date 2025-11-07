from sqlalchemy import Column, Integer, Float, JSON
from . import Base

class DeckStats(Base):
    __tablename__ = 'deck_statistics'

    deck_id = Column(Integer, primary_key=True)
    total_tests = Column(Integer, default=0, nullable=False)
    avg_score = Column(Float, default=0.0, nullable=False)
    success_rate = Column(Float, default=0.0, nullable=False)
    avg_time_ms = Column(Integer, default=0, nullable=False)
    card_stats = Column(JSON, nullable=True)

