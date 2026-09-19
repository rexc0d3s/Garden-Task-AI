"""Pydantic request/response schemas for the AI Garden API."""
import datetime as dt
from typing import Optional, List

from pydantic import BaseModel, Field


# ---------- Skills ----------

class SkillOut(BaseModel):
    id: int
    name: str
    slug: str
    xp: int
    garden_area: str
    stage: str
    next_stage: Optional[str]
    progress_to_next: float

    class Config:
        from_attributes = True


# ---------- Tasks ----------

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    skill_id: int
    difficulty: str = Field(..., pattern="^(easy|medium|hard|expert)$")


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    skill_id: int
    skill_name: str
    difficulty: str
    xp_value: int
    completed: bool
    created_at: dt.datetime
    completed_at: Optional[dt.datetime]

    class Config:
        from_attributes = True


class TaskCompleteResult(BaseModel):
    task: TaskOut
    xp_awarded: int
    leveled_up: bool
    new_level: int
    unlocked_achievements: List[str]


# ---------- Dashboard ----------

class ProfileOut(BaseModel):
    level: int
    total_xp: int
    xp_into_level: int
    xp_for_next_level: int
    current_streak: int
    longest_streak: int
    tasks_completed: int


class DashboardOut(BaseModel):
    profile: ProfileOut
    skills: List[SkillOut]
    recent_tasks: List[TaskOut]
    achievements_unlocked: int
    achievements_total: int


# ---------- Achievements ----------

class AchievementOut(BaseModel):
    key: str
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: Optional[dt.datetime]

    class Config:
        from_attributes = True


# ---------- Assistant ----------

class AssistantRequest(BaseModel):
    message: str
    mode: str = Field(
        default="chat",
        pattern="^(chat|recommend_task|weak_skills|explain|cyber_quiz|project_ideas|summary)$",
    )


class AssistantResponse(BaseModel):
    reply: str
    mode: str
