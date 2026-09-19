"""
SQLAlchemy ORM models for AI Garden.

Tables:
- Skill: the five skill categories and their accumulated XP
- Task: user-created technical tasks tied to a skill + difficulty
- UserProfile: single-row table holding level/total XP/streak state
- Achievement: milestone definitions and unlock state
"""
import datetime as dt

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)  # e.g. "python"
    xp = Column(Integer, default=0, nullable=False)
    # garden_area maps this skill to a plot/quadrant in the garden visualization
    garden_area = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="skill")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="", nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    difficulty = Column(String, nullable=False)  # easy | medium | hard | expert
    xp_value = Column(Integer, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    skill = relationship("Skill", back_populates="tasks")


class UserProfile(Base):
    """Single-row table (id=1) tracking overall progress and streak state."""
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, default=1)
    total_xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_active_date = Column(DateTime, nullable=True)


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)  # stable identifier, e.g. "first_sprout"
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    icon = Column(String, default="🌱")
    unlocked = Column(Boolean, default=False, nullable=False)
    unlocked_at = Column(DateTime, nullable=True)
