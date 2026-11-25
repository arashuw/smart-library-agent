from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime, timezone
from .database import Base

class UserBook(Base):
    __tablename__ = "user_books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(150), nullable=False)
    status = Column(String(50), default="read")
    rating = Column(Float, nullable=True)
    review = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class BookInsight(Base):
    __tablename__ = "book_insights"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), unique=True, index=True, nullable=False)
    author = Column(String(150), nullable=False)
    spoiler_free_summary = Column(Text, nullable=False)
    vibe_tags = Column(String(250), nullable=True)
    target_audience = Column(Text, nullable=True)
    cover_url = Column(String(500), nullable=True)