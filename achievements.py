from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Achievement
from app.schemas import AchievementOut

router = APIRouter(prefix="/api/achievements", tags=["achievements"])


@router.get("", response_model=list[AchievementOut])
def list_achievements(db: Session = Depends(get_db)):
    return db.query(Achievement).order_by(Achievement.id).all()
