"""
Business logic: task completion, XP awarding, streak tracking, and
achievement unlocking. Kept separate from routers so routes stay thin.
"""
import datetime as dt
from typing import List

from sqlalchemy.orm import Session

from app.models import Skill, Task, UserProfile, Achievement
from app.xp import DIFFICULTY_XP, compute_level, growth_stage_for_xp


def get_profile(db: Session) -> UserProfile:
    profile = db.query(UserProfile).filter_by(id=1).first()
    if not profile:
        profile = UserProfile(id=1)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def _update_streak(db: Session, profile: UserProfile) -> None:
    """Update the daily streak based on today's date vs last_active_date."""
    today = dt.date.today()
    last = profile.last_active_date.date() if profile.last_active_date else None

    if last == today:
        return  # already counted today
    elif last == today - dt.timedelta(days=1):
        profile.current_streak += 1
    else:
        profile.current_streak = 1

    profile.longest_streak = max(profile.longest_streak, profile.current_streak)
    profile.last_active_date = dt.datetime.utcnow()


def _check_achievements(db: Session, skill: Skill, profile: UserProfile,
                         tasks_completed: int, skill_xp_before: int) -> List[str]:
    """Check milestone conditions and unlock any newly-earned achievements."""
    unlocked_now = []

    def unlock(key: str):
        ach = db.query(Achievement).filter_by(key=key).first()
        if ach and not ach.unlocked:
            ach.unlocked = True
            ach.unlocked_at = dt.datetime.utcnow()
            unlocked_now.append(ach.name)

    # First Sprout: any skill crosses from "seed" into "sprout" or beyond
    if skill_xp_before < 50 <= skill.xp:
        unlock("first_sprout")

    if profile.level >= 5:
        unlock("level_5")

    if tasks_completed >= 10:
        unlock("tasks_10")
    if tasks_completed >= 25:
        unlock("tasks_25")

    if skill.slug == "ai-engineering":
        unlock("first_ai_project")
    if skill.slug == "cybersecurity":
        unlock("first_cyber_challenge")
    if skill.slug == "digital-forensics":
        unlock("first_forensics_case")

    if profile.current_streak >= 7:
        unlock("streak_7")
    if profile.current_streak >= 30:
        unlock("streak_30")

    return unlocked_now


def complete_task(db: Session, task: Task) -> dict:
    """
    Mark a task complete, award XP to its skill and the overall profile,
    update the level/streak, and unlock any achievements this triggers.
    """
    if task.completed:
        return {
            "xp_awarded": 0, "leveled_up": False,
            "new_level": get_profile(db).level, "unlocked_achievements": [],
        }

    skill = db.query(Skill).filter_by(id=task.skill_id).first()
    profile = get_profile(db)

    skill_xp_before = skill.xp
    level_before = compute_level(profile.total_xp)["level"]

    task.completed = True
    task.completed_at = dt.datetime.utcnow()

    skill.xp += task.xp_value
    profile.total_xp += task.xp_value
    _update_streak(db, profile)

    level_info = compute_level(profile.total_xp)
    profile.level = level_info["level"]
    leveled_up = profile.level > level_before

    tasks_completed = db.query(Task).filter_by(completed=True).count()

    unlocked = _check_achievements(db, skill, profile, tasks_completed, skill_xp_before)

    db.commit()
    db.refresh(task)
    db.refresh(skill)
    db.refresh(profile)

    return {
        "xp_awarded": task.xp_value,
        "leveled_up": leveled_up,
        "new_level": profile.level,
        "unlocked_achievements": unlocked,
    }


def xp_value_for_difficulty(difficulty: str) -> int:
    return DIFFICULTY_XP[difficulty]
