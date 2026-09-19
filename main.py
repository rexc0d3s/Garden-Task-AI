"""
AI Garden backend entrypoint.

Creates the FastAPI app, sets up CORS, creates tables + seed data on
startup, and mounts all routers.
"""
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app.seed import seed_database
from app.routers import dashboard, tasks, skills, achievements, assistant

load_dotenv()

app = FastAPI(
    title="AI Garden API",
    description="Backend for AI Garden — a gamified personal growth dashboard.",
    version="1.0.0",
)

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


app.include_router(dashboard.router)
app.include_router(tasks.router)
app.include_router(skills.router)
app.include_router(achievements.router)
app.include_router(assistant.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
