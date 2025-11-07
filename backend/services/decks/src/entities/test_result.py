from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, JSON, func
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

from . import Base

class TestResult(Base):
    __tablename__ = 'test_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    deck_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    total_time_ms = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    card_results = relationship("TestResultCard", back_populates="test_result", cascade="all, delete-orphan")
