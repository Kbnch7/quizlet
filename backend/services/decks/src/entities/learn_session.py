from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, func
from . import Base


class LearnSession(Base):
    __tablename__ = "learn_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    deck_id = Column(
        Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False
    )
    status = Column(String(32), default="active", nullable=False)
    started_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at = Column(DateTime(timezone=True), nullable=True)
    total_cards = Column(Integer, default=0, nullable=False)
    learned_cards = Column(Integer, default=0, nullable=False)
