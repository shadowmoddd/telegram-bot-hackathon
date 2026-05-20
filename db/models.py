from datetime import datetime
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float,
    ForeignKey, Integer, String, Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)

    topic = Column(String, nullable=True)
    level = Column(String, nullable=True)
    format_pref = Column(String, nullable=True)
    time_available = Column(String, nullable=True)

    current_position = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    route_items = relationship("UserRoute", back_populates="user", cascade="all, delete-orphan")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String, nullable=False)   # stepik | youtube | habr | manual
    topic = Column(String, nullable=False)
    level = Column(String, nullable=False)    # beginner | intermediate | advanced
    format = Column(String, nullable=False)   # course | video | article
    duration_h = Column(Float, nullable=True)
    rating = Column(Float, default=0.0)
    thumbnail_url = Column(String, nullable=True)
    is_free = Column(Boolean, default=True)
    language = Column(String, default="ru")
    created_at = Column(DateTime, default=datetime.utcnow)


class UserRoute(Base):
    __tablename__ = "user_routes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    position = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending | completed | skipped

    user = relationship("User", back_populates="route_items")
    resource = relationship("Resource")
