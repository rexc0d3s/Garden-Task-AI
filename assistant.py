"""
Garden AI: an assistant endpoint that gives Claude the user's stored
progress as context, then answers in one of several modes (free chat,
task recommendation, weak-skill analysis, concept explanations,
cybersecurity quiz questions, project ideas, or an encouraging summary).

The Anthropic API key lives only in the backend's environment (.env) and
is never sent to or stored in the frontend, per the project's security
requirements.
"""
import os
import json

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Skill, Task, Achievement
from app.crud import get_profile
from app.xp import compute_level, growth_progress
from app.schemas import AssistantRequest, AssistantResponse

router = APIRouter(prefix="/api/assistant", tags=["assistant"])

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

MODE_INSTRUCTIONS = {
    "chat": "Answer the user's message helpfully, in the voice of a warm, "
            "knowledgeable mentor called Garden AI.",
    "recommend_task": "Recommend ONE specific next task the user should tackle, "
                       "with a brief reason tied to their weakest or most stagnant skill. "
                       "Keep it concrete and actionable.",
    "weak_skills": "Identify which 1-2 skills need the most attention right now "
                   "based on their relative XP, and explain why, plus one concrete "
                   "suggestion per skill.",
    "explain": "Explain the technical concept the user is asking about, clearly "
               "and at an appropriate depth for someone actively learning it.",
    "cyber_quiz": "Generate 3 cybersecurity practice questions (mix of conceptual "
                  "and applied) appropriate to the user's current cybersecurity "
                  "progress level. Include the answer after each question, clearly marked.",
    "project_ideas": "Suggest 3 project ideas spanning the user's skills, scaled "
                     "to their current level, each with a one-line description of "
                     "what it would demonstrate.",
    "summary": "Give a short, genuinely encouraging progress summary covering "
               "overall level, streak, and standout skill growth.",
}


def _build_context(db: Session) -> str:
    profile = get_profile(db)
    level_info = compute_level(profile.total_xp)
    skills = db.query(Skill).all()
    tasks_completed = db.query(Task).filter_by(completed=True).count()
    achievements_unlocked = db.query(Achievement).filter_by(unlocked=True).count()
    achievements_total = db.query(Achievement).count()

    skill_lines = []
    for s in skills:
        gp = growth_progress(s.xp)
        skill_lines.append(
            f"- {s.name}: {s.xp} XP, stage={gp['stage']} "
            f"({gp['progress_to_next']*100:.0f}% to {gp['next_stage'] or 'max stage'})"
        )

    context = f"""
User progress in AI Garden (a gamified learning dashboard):
- Level: {level_info['level']} ({level_info['xp_into_level']}/{level_info['xp_for_next_level']} XP into level)
- Total XP: {profile.total_xp}
- Current streak: {profile.current_streak} days (longest: {profile.longest_streak})
- Tasks completed: {tasks_completed}
- Achievements unlocked: {achievements_unlocked}/{achievements_total}

Skill breakdown:
{chr(10).join(skill_lines)}
""".strip()
    return context


@router.post("", response_model=AssistantResponse)
async def ask_garden_ai(payload: AssistantRequest, db: Session = Depends(get_db)):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    if not api_key or api_key.strip() == "" or api_key == "your-key-here":
        raise HTTPException(
            status_code=503,
            detail="Garden AI is not configured. Add a real ANTHROPIC_API_KEY in backend/.env (not the placeholder value).",
        )

    context = _build_context(db)
    instruction = MODE_INSTRUCTIONS.get(payload.mode, MODE_INSTRUCTIONS["chat"])

    system_prompt = (
        "You are Garden AI, the encouraging but technically sharp AI mentor "
        "embedded in a personal-growth dashboard called AI Garden, for someone "
        "learning Python, AI engineering, cybersecurity, digital forensics, and "
        "software engineering. Use the user's stored progress as context for "
        "every answer. Be concise, concrete, and avoid generic filler."
    )

    user_content = f"{context}\n\nTask for you: {instruction}\n\nUser message: {payload.message}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                ANTHROPIC_API_URL,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 1000,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_content}],
                },
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"Anthropic API error: {e.response.text}")
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Could not reach Anthropic API: {e}")

    data = resp.json()
    text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    reply = "\n".join(text_blocks).strip() or "Garden AI had nothing to say — try rephrasing."

    return AssistantResponse(reply=reply, mode=payload.mode)
