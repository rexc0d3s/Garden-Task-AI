from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task, Skill
from app.schemas import TaskCreate, TaskOut, TaskCompleteResult
from app.crud import complete_task, xp_value_for_difficulty

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _to_task_out(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id, title=task.title, description=task.description,
        skill_id=task.skill_id, skill_name=task.skill.name,
        difficulty=task.difficulty, xp_value=task.xp_value,
        completed=task.completed, created_at=task.created_at,
        completed_at=task.completed_at,
    )


@router.get("", response_model=list[TaskOut])
def list_tasks(completed: bool | None = None, db: Session = Depends(get_db)):
    q = db.query(Task)
    if completed is not None:
        q = q.filter(Task.completed == completed)
    tasks = q.order_by(Task.created_at.desc()).all()
    return [_to_task_out(t) for t in tasks]


@router.post("", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter_by(id=payload.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    task = Task(
        title=payload.title,
        description=payload.description,
        skill_id=payload.skill_id,
        difficulty=payload.difficulty,
        xp_value=xp_value_for_difficulty(payload.difficulty),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _to_task_out(task)


@router.post("/{task_id}/complete", response_model=TaskCompleteResult)
def mark_task_complete(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter_by(id=task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    result = complete_task(db, task)
    return TaskCompleteResult(task=_to_task_out(task), **result)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter_by(id=task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
