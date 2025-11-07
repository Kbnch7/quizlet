from sqlalchemy import Column, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from . import Base

class TestResultCard(Base):
    __tablename__ = 'test_result_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_result_id = Column(Integer, ForeignKey('test_results.id', ondelete='CASCADE'), nullable=False)
    card_id = Column(Integer, nullable=False)
    correct = Column(Boolean, nullable=False)
    answer_time_ms = Column(Integer, nullable=False)
    user_answer = Column(Text, nullable=True)

    test_result = relationship("TestResult", back_populates="card_results")
