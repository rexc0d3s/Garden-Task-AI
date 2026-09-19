[README.md](https://github.com/user-attachments/files/32426191/README.md)
🌱 AI Garden

A gamified personal-growth dashboard for tracking progress in Python, AI
engineering, cybersecurity, digital forensics, and software engineering.
Every completed task earns XP; XP grows a virtual plant for that skill,
from a bare **Seed** all the way up to a full **Tree**. An AI mentor
("Garden AI") sits alongside your progress and can recommend what to work
on next, quiz you, explain concepts, or just cheer you on.

---

## What it does

- **Dashboard** — level, total XP, XP to next level, streak, tasks
  completed, skill progress, and the garden itself, all in one view.
- **Tasks** — create a task, assign it to a skill, set a difficulty
  (Easy/Medium/Hard/Expert), and mark it complete to earn XP.
- **Garden** — a visual scene where each of the five skills occupies its
  own plot and renders as a plant at one of six growth stages:
  `Seed → Sprout → Plant → Flower → Mature Plant → Tree`.
- **Achievements** — milestones like *First Sprout*, *Level 5*, task
  count milestones, first task in each specialty skill, and 7/30-day
  streaks, unlocked automatically as you play.
- **Garden AI** — an assistant with access to your live stored progress
  (level, XP, streak, per-skill growth) that can recommend a next task,
  flag which skills need attention, explain a concept, generate
  cybersecurity practice questions, suggest project ideas, or summarize
  your progress encouragingly.

---

## Architecture

```
ai-garden/
├── backend/            FastAPI + SQLite REST API
│   └── app/
│       ├── main.py         App entrypoint, CORS, startup seeding
│       ├── database.py     SQLAlchemy engine/session
│       ├── models.py       Skill, Task, UserProfile, Achievement tables
│       ├── schemas.py      Pydantic request/response models
│       ├── xp.py           XP, leveling curve, growth-stage thresholds
│       ├── crud.py         Task completion, streaks, achievement unlocks
│       ├── seed.py         Seeds the 5 skills + achievement definitions
│       ├── achievements_data.py
│       └── routers/
│           ├── dashboard.py
│           ├── tasks.py
│           ├── skills.py
│           ├── achievements.py
│           └── assistant.py   Garden AI — calls the Anthropic API server-side
└── frontend/           React + Vite + Tailwind CSS
    └── src/
        ├── api/client.js       Thin fetch wrapper around the REST API
        ├── skillTheme.js       Per-skill colors/emoji/garden-plot names
        ├── components/         Card, NavBar, PlantIllustration (SVG),
        │                       StatStrip, SkillCard, GardenView,
        │                       TaskForm, TaskList, AchievementsPanel,
        │                       GardenAIPanel
        └── pages/              DashboardPage, TasksPage, GardenPage,
                                 AchievementsPage, AssistantPage
```

The frontend and backend are fully separate processes that talk over a
REST API (`http://localhost:8000/api/...` by default). The frontend never
holds an API key — all calls to Anthropic happen inside the FastAPI
backend, which reads `ANTHROPIC_API_KEY` from its own environment.

### Data model

- `Skill` — name, slug, accumulated XP, garden plot.
- `Task` — title, description, skill, difficulty, XP value, completed flag.
- `UserProfile` — single-row table holding total XP, level, current/longest streak.
- `Achievement` — key, name, description, icon, unlocked state.

### Game math (`backend/app/xp.py`)

- XP per difficulty: Easy 20, Medium 40, Hard 75, Expert 150.
- Level curve: leveling from level *N* to *N+1* costs `100 + (N-1)*50` XP
  (so it gets gradually harder, without ever requiring a lookup table).
- Growth-stage thresholds (per-skill XP): Seed 0, Sprout 50, Plant 150,
  Flower 300, Mature Plant 500, Tree 800.

---

## Tech stack

**Frontend:** React 19, Vite, Tailwind CSS (dark mode via `class` strategy)
**Backend:** Python, FastAPI, SQLAlchemy, Uvicorn
**Database:** SQLite (file-based, zero setup)
**AI:** Anthropic API (Claude), called only from the backend

---

## How to run it

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env if you want Garden AI to work
uvicorn app.main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`. Interactive docs are at
`http://localhost:8000/docs`. On first startup it creates `ai_garden.db`
and seeds the 5 skills + achievement list automatically.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env            # defaults to http://localhost:8000, adjust if needed
npm run dev
```

Open `http://localhost:5173`.

### 3. Build for production

```bash
cd frontend
npm run build      # outputs static files to frontend/dist/
```

Serve `frontend/dist/` with any static host, and run the backend behind
a process manager (e.g. `uvicorn` + `systemd`, or a container). Update
`CORS_ORIGINS` in the backend `.env` to match your deployed frontend URL.

---

## Environment variables

### `backend/.env`

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./ai_garden.db` |
| `ANTHROPIC_API_KEY` | Key used server-side for Garden AI. Without it, the assistant endpoint returns a clear 503 rather than failing silently. | *(required for Garden AI)* |
| `ANTHROPIC_MODEL` | Which Claude model to call | `claude-sonnet-4-6` |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins | `http://localhost:5173` |

### `frontend/.env`

| Variable | Purpose | Default |
|---|---|---|
| `VITE_API_URL` | Base URL of the backend API | `http://localhost:8000` |

No API keys are ever stored in frontend code or shipped to the browser.

---

## Features implemented (MVP)

- [x] Dashboard: level, total XP, XP-to-next-level, streak, tasks completed, skill progress, garden
- [x] Task CRUD: create, list, filter, complete, delete
- [x] XP system with 4 difficulty tiers
- [x] Garden visualization with per-skill plots and growth-stage art
- [x] 5 independently tracked skills, each with its own garden area
- [x] 9 achievements with automatic unlock logic
- [x] Garden AI assistant (7 modes) using live stored progress as context
- [x] Cozy pastel UI, rounded cards, soft shadows, subtle animations, dark mode, responsive layout

## Future improvements

- Multi-user auth (the current single-profile model assumes one user)
- Task editing and due dates / reminders
- Weekly/monthly progress charts (XP over time, per-skill trends)
- More granular achievement tiers (e.g. per-skill mastery badges)
- Persisted Garden AI chat history per session
- Migrate from SQLite to Postgres for multi-user/production deployments
- Export progress as a shareable "garden snapshot" image
- Seasonal/cosmetic garden themes unlocked by milestones
