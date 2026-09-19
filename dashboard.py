from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task, Achievement
from app.schemas import DashboardOut, ProfileOut
from app.crud import get_profile
from app.xp import compute_level
from app.routers.skills import _to_skill_out
from app.routers.tasks import _to_task_out
from app.models import Skill

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    profile = get_profile(db)
    level_info = compute_level(profile.total_xp)

    tasks_completed = db.query(Task).filter_by(completed=True).count()
    recent_tasks = (
        db.query(Task).order_by(Task.created_at.desc()).limit(5).all()
    )
    skills = db.query(Skill).all()

    achievements_unlocked = db.query(Achievement).filter_by(unlocked=True).count()
    achievements_total = db.query(Achievement).count()

    return DashboardOut(
        profile=ProfileOut(
            level=level_info["level"],
            total_xp=profile.total_xp,
            xp_into_level=level_info["xp_into_level"],
            xp_for_next_level=level_info["xp_for_next_level"],
            current_streak=profile.current_streak,
            longest_streak=profile.longest_streak,
            tasks_completed=tasks_completed,
        ),
        skills=[_to_skill_out(s) for s in skills],
        recent_tasks=[_to_task_out(t) for t in recent_tasks],
        achievements_unlocked=achievements_unlocked,
        achievements_total=achievements_total,
    )
