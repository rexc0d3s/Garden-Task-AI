from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Skill
from app.schemas import SkillOut
from app.xp import growth_progress

router = APIRouter(prefix="/api/skills", tags=["skills"])


def _to_skill_out(skill: Skill) -> SkillOut:
    gp = growth_progress(skill.xp)
    return SkillOut(
        id=skill.id, name=skill.name, slug=skill.slug, xp=skill.xp,
        garden_area=skill.garden_area, stage=gp["stage"],
        next_stage=gp["next_stage"], progress_to_next=gp["progress_to_next"],
    )


@router.get("", response_model=list[SkillOut])
def list_skills(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    return [_to_skill_out(s) for s in skills]
