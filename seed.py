"""Seed initial skills, the singleton user profile, and achievements."""
from sqlalchemy.orm import Session

from app.models import Skill, UserProfile, Achievement
from app.achievements_data import ACHIEVEMENTS

INITIAL_SKILLS = [
    {"name": "Python", "slug": "python", "garden_area": "north-bed"},
    {"name": "AI Engineering", "slug": "ai-engineering", "garden_area": "greenhouse"},
    {"name": "Cybersecurity", "slug": "cybersecurity", "garden_area": "east-hedge"},
    {"name": "Digital Forensics", "slug": "digital-forensics", "garden_area": "stone-path"},
    {"name": "Software Engineering", "slug": "software-engineering", "garden_area": "west-orchard"},
]


def seed_database(db: Session) -> None:
    if db.query(Skill).count() == 0:
        for s in INITIAL_SKILLS:
            db.add(Skill(**s, xp=0))

    if db.query(UserProfile).count() == 0:
        db.add(UserProfile(id=1, total_xp=0, level=1, current_streak=0, longest_streak=0))

    if db.query(Achievement).count() == 0:
        for a in ACHIEVEMENTS:
            db.add(Achievement(**a, unlocked=False))

    db.commit()
