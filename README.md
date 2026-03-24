# Skilio 🌌🌊🌲

> **Scenario-Based Life Skills Learning Platform for Children**  
> Children navigate branching story worlds and make real safety decisions. Parents track every choice in real time.

![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-default-003B57?style=flat-square&logo=sqlite)
![MySQL](https://img.shields.io/badge/MySQL-supported-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-pytest-blue?style=flat-square)

---

## Screenshots

### Login — Split-panel with JWT authentication
![Login](screenshots/01-login.svg)

### Parent Dashboard — Child XP cards and API overview
![Dashboard](screenshots/02-dashboard.svg)

### Scenario Player — Branching DAG with NPC dialogue
![Scenario Player](screenshots/03-scenario-player.svg)

---

## What is Skilio?

Traditional child safety education is passive — children memorise rules but never practice decisions. Skilio replaces that with a **scenario engine**: a directed acyclic graph (DAG) of story nodes where children navigate realistic safety situations, make choices, and see consequences. Parents get a full audit trail of every decision.

### The Three Worlds

| 🌌 Outer Space | 🌊 The Deep Sea | 🌲 Enchanted Forest |
|:---:|:---:|:---:|
| Safe routes vs risky shortcuts | Stranger danger, secrets, asking for help | Trusted adults, fire safety, instinct |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI 0.111 + Python 3.11 |
| ORM | SQLAlchemy 2.0 (Mapped[] type annotations) |
| Migrations | Alembic |
| **Database** | **SQLite (default) · MySQL · PostgreSQL** |
| Auth | JWT HS256 + bcrypt + httpOnly refresh cookies |
| Frontend | React 18 + Vite 5 + TypeScript |
| State | TanStack React Query 5 + Zustand 4 |

---

## Data Model — 12 Entities

```
User ──< Child ──< ScenarioAttempt ──< ScenarioAttemptChoice
           │               │                     │
           │       ScenarioChoice ───────────────┘
           │
SkillModule ──< Lesson ──< ScenarioNode
                                │
                         next_node_id ──► ScenarioNode   ← SELF-REFERENTIAL DAG

Child ──< Progress    (one row per child per module)
Child ──< BadgeAward ──> Badge
User  ──< RefreshToken  (hashed, single-use rotation)
```

**Advanced relationships:**
- **Self-referential DAG** — `ScenarioNode → ScenarioChoice → ScenarioNode` (next_node_id)
- **Audit trail** — `ScenarioAttemptChoice` records every individual decision
- **Ownership enforcement** — every child endpoint checks `child.parent_id == user.id`

---

## Quickstart — Zero Config (SQLite)

### Backend

```bash
cd backend

# Windows:
python -m venv .venv && .venv\Scripts\activate
# Mac/Linux:
python -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt

# No .env needed — SQLite is the default
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/docs  (Swagger UI)
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

**Demo login:** `demo@skilio.com` / `Demo1234!`

---

## Switch to MySQL (for extra marks)

Create `backend/.env`:
```
DATABASE_URL=mysql+pymysql://skilio:skiliopass@localhost:3306/skilio_db
```

No code changes — the engine adapts automatically.

---

## Run Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

---

## Security Model

| Layer | Implementation |
|---|---|
| Passwords | bcrypt — timing-attack safe, slow by design |
| Access token | JWT HS256 · 30 min · Zustand memory only — **never localStorage** |
| Refresh token | JWT · 7 days · httpOnly cookie · SHA-256 hashed in DB |
| Rotation | Each `/refresh` revokes old token and issues new pair |
| Reuse detection | Revoked token replayed → **all user tokens wiped** |
| Ownership | `child.parent_id == user.id` enforced in `Depends()` |
| Enumeration | 404 for both "not found" and "wrong owner" |
| Rate limiting | 10 logins/min, 5 registrations/min per IP |
| Size limiting | 1 MB max request body (DoS protection) |
| Input sanitisation | Pydantic + regex blocks `< > " ' % ; ( ) &` |

---

## API Reference — 24 Endpoints

Full interactive docs at **http://localhost:8000/docs**

| Router | Routes | Description |
|---|---|---|
| `/api/auth` | 5 | register, login, refresh, logout, me |
| `/api/children` | 9 | CRUD + progress, badges, attempts, summary |
| `/api/modules` | 2 | world listing with age filter |
| `/api/lessons` | 1 | lesson detail |
| `/api/scenarios` | 5 | DAG engine: start, choose, history, resume |
| `/api/badges` | 2 | badge catalogue |

---

## Team

| Name | Role |
|---|---|
| **Ranim** | Co-Founder · Product Architect · Chief Technical Lead |
| **Bochra** | Co-Founder · Backend Lead · Operations & Presentation Lead |
| **Imad** | Backend Engineer — API & Validation |
| **Mazid** | Data Engineer — Database & Entity Design |
| **Mohammed** | Documentation & GitHub Manager |
