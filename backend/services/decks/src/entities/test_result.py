from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship

from . import Base


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deck_id = Column(
        Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Integer, nullable=False)
    total_time_seconds = Column(Integer, nullable=False)
    correct_rate = Column(Float, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    card_results = relationship(
        "CardResult",
        back_populates="test_result",
        cascade="all, delete-orphan",
    )
