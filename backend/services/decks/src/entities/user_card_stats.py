from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Boolean
from . import Base


class UserCardStats(Base):
    __tablename__ = "user_card_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    card_id = Column(
        Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False
    )
    success_count = Column(Integer, default=0, nullable=False)
    fail_count = Column(Integer, default=0, nullable=False)
    total_answers = Column(Integer, default=0, nullable=False)
    correct_rate = Column(Float, default=0.0, nullable=False)
    streak = Column(Integer, default=0, nullable=False)
    difficulty_score = Column(Float, default=0.5, nullable=False)
    is_learned = Column(Boolean, default=False, nullable=False)
    last_result = Column(Boolean, nullable=True)
    last_answered_at = Column(DateTime(timezone=True), nullable=True)
