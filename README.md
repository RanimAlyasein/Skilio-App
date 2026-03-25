# Skilio 🌌🌊🌲

> **Scenario-Based Life Skills Learning Platform for Children**  
> Children navigate branching story worlds and make real safety decisions. Parents track every choice in real time.

![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-default-003B57?style=flat-square&logo=sqlite)
![MySQL](https://img.shields.io/badge/MySQL-supported-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-pytest-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Table of Contents

- [What is Skilio?](#what-is-skilio)
- [The Three Worlds](#the-three-worlds)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Model](#data-model--13-entities)
- [Quickstart](#quickstart--zero-config-sqlite)
- [Docker Setup](#docker-setup-full-stack)
- [Switch to MySQL](#switch-to-mysql)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference--27-endpoints)
- [Security Model](#security-model)
- [Running Tests](#running-tests)
- [Team](#team)

---

## What is Skilio?

Traditional child safety education is **passive** — children memorise rules but never practice decisions. Skilio replaces that with a **scenario engine**: a directed acyclic graph (DAG) of story nodes where children navigate realistic safety situations, make choices, and see consequences. Parents get a full audit trail of every decision.

### Key Features

- 🎮 **Branching scenario engine** — DAG-based story nodes with NPC dialogue and multiple-choice decisions
- 👨‍👩‍👧 **Parent dashboard** — real-time tracking of each child's progress, XP, and badge awards
- 🏅 **Gamification** — XP system, skill badges, and module completion rewards
- 🔐 **Production-grade auth** — JWT access tokens + httpOnly refresh cookies with rotation and reuse detection
- 🌍 **Multi-database** — SQLite (zero config), MySQL, or PostgreSQL — switched via a single env variable
- 🐳 **Docker-ready** — full stack compose file included

---

## The Three Worlds

| 🌌 Outer Space | 🌊 The Deep Sea | 🌲 Enchanted Forest |
|:---:|:---:|:---:|
| Safe routes vs risky shortcuts | Stranger danger, secrets, asking for help | Trusted adults, fire safety, instinct |

Each world contains age-appropriate scenarios designed for children aged **4–17**, grouped into skill modules with structured lessons.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI 0.111 + Python 3.11 |
| **ORM** | SQLAlchemy 2.0 (Mapped[] type annotations) |
| **Migrations** | Alembic |
| **Database** | SQLite (default) · MySQL · PostgreSQL |
| **Auth** | JWT HS256 + bcrypt + httpOnly refresh cookies |
| **Frontend** | React 18 + Vite 5 + TypeScript |
| **State Management** | TanStack React Query 5 + Zustand 4 |
| **Routing** | React Router v6 |
| **HTTP Client** | Axios with 401 interceptor |
| **Styling** | Tailwind CSS 3 |
| **Testing** | pytest + httpx |
| **Containerisation** | Docker + Docker Compose |

---

## Project Structure

```
skilio/
├── skilio-backend/
│   ├── app/
│   │   ├── api/              # Route handlers (auth, users, children, scenarios, modules, badges, lessons)
│   │   ├── core/             # Config, database, security, dependencies
│   │   ├── crud/             # Database CRUD operations
│   │   ├── models/           # SQLAlchemy ORM models (13 entities)
│   │   ├── schemas/          # Pydantic v2 request/response schemas
│   │   ├── services/         # Business logic (auth, badge, scenario, progress, child)
│   │   └── main.py           # FastAPI application factory
│   ├── alembic/              # Database migration files
│   ├── scripts/
│   │   └── seed.py           # Database seeder with demo data
│   ├── tests/                # pytest test suite
│   ├── screenshots/          # UI preview SVGs
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
│
└── skilio-frontend/
    ├── src/                  # React + TypeScript source
    ├── package.json
    ├── nginx.conf            # Production static file server config
    └── Dockerfile
```

---

## Data Model — 13 Entities

```
User ──< Child ──< ScenarioAttempt ──< ScenarioAttemptChoice
  │          │              │                    │
  │          │       ScenarioChoice ─────────────┘
  │          │
  │          ├──< BadgeAward ──> Badge ──< ModuleBadge ──> SkillModule
  │          │                                                  │
  │          ├──< Progress                          SkillModule ──< Lesson ──< ScenarioNode
  │          │                                                                      │
  └──< RefreshToken                                             next_node_id ──► ScenarioNode
                                                                           ← SELF-REFERENTIAL DAG
```

**Advanced relationships:**
- **Self-referential DAG** — `ScenarioNode → ScenarioChoice → ScenarioNode` (next_node_id)
- **Full audit trail** — `ScenarioAttemptChoice` records every individual decision a child makes
- **Many-to-many** — `Badge ↔ SkillModule` via `ModuleBadge` association table
- **Ownership enforcement** — every child endpoint verifies `child.parent_id == user.id`

---

## Quickstart — Zero Config (SQLite)

No database server required. SQLite is the default — just clone and run.

### Prerequisites

- Python 3.11+
- Node.js 18+

### Backend

```bash
cd skilio-backend

# Create and activate virtual environment
# Windows:
python -m venv .venv && .venv\Scripts\activate
# Mac/Linux:
python -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt

# No .env needed — SQLite works out of the box
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

**Backend is live at:** `http://localhost:8000`  
**Swagger UI:** `http://localhost:8000/docs`  
**ReDoc:** `http://localhost:8000/redoc`

### Frontend

```bash
cd skilio-frontend
npm install
npm run dev
```

**Frontend is live at:** `http://localhost:5173`

### Demo Credentials

```
Email:    demo@skilio.com
Password: Demo1234!
```

---

## Docker Setup (Full Stack)

The Docker Compose file spins up MySQL + FastAPI backend + React frontend in one command.

```bash
cd skilio-backend

# Optional: create a .env file to override secrets
cp .env.example .env

docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:80 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| MySQL | localhost:3306 |

To stop and remove containers:

```bash
docker compose down
```

To rebuild after code changes:

```bash
docker compose up --build --force-recreate
```

---

## Switch to MySQL

Create `skilio-backend/.env` with the following content:

```env
DATABASE_URL=mysql+pymysql://skilio:skiliopass@localhost:3306/skilio_db
```

No code changes needed — the database engine adapts automatically via `DATABASE_URL`. PostgreSQL is also supported:

```env
DATABASE_URL=postgresql://skilio:skiliopass@localhost:5432/skilio_db
```

---

## Environment Variables

Copy `.env.example` to `.env` in the backend directory. All variables are optional — the app runs with SQLite and safe defaults without any `.env` file.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./skilio.db` | Database connection string |
| `SECRET_KEY` | `skilio-dev-secret-key-...` | JWT signing key — **change in production** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `ALLOWED_ORIGINS` | `http://localhost:5173,...` | CORS allowed origins |
| `DEBUG` | `false` | Enable debug mode |

> ⚠️ **Never commit `.env` to version control.** The `.gitignore` excludes it by default.

To generate a strong `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## API Reference — 27 Endpoints

Full interactive documentation is available at **`http://localhost:8000/docs`** (Swagger UI).

| Method | Path | Router | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | Auth | Register a new parent account |
| `POST` | `/api/auth/login` | Auth | Login and receive access + refresh tokens |
| `POST` | `/api/auth/refresh` | Auth | Rotate refresh token and issue new access token |
| `POST` | `/api/auth/logout` | Auth | Revoke current refresh token |
| `GET` | `/api/auth/me` | Auth | Get current authenticated user |
| `GET` | `/api/users/me` | Users | Read own profile |
| `PUT` | `/api/users/me` | Users | Update own full name |
| `DELETE` | `/api/users/me` | Users | Soft-deactivate own account |
| `GET` | `/api/children/` | Children | List all children for the current parent |
| `POST` | `/api/children/` | Children | Add a new child profile |
| `GET` | `/api/children/{id}` | Children | Get child details |
| `PUT` | `/api/children/{id}` | Children | Update child profile |
| `DELETE` | `/api/children/{id}` | Children | Delete child profile (soft) |
| `GET` | `/api/children/{id}/progress` | Children | Child module progress summary |
| `GET` | `/api/children/{id}/badges` | Children | Badges earned by child |
| `GET` | `/api/children/{id}/attempts` | Children | Scenario attempt history |
| `GET` | `/api/children/{id}/summary` | Children | XP, progress, and badges in one request |
| `GET` | `/api/modules/` | Modules | List skill worlds (optional `?age=` filter) |
| `GET` | `/api/modules/{id}` | Modules | World detail with lessons |
| `GET` | `/api/lessons/{id}` | Lessons | Lesson detail with scenario entry point |
| `POST` | `/api/scenarios/attempts` | Scenarios | Start or resume a scenario attempt |
| `GET` | `/api/scenarios/attempts/{id}` | Scenarios | Get current attempt state |
| `POST` | `/api/scenarios/attempts/{id}/choose` | Scenarios | Submit a choice and advance the DAG |
| `GET` | `/api/scenarios/attempts/{id}/history` | Scenarios | Full choice audit trail |
| `GET` | `/api/scenarios/nodes/{id}` | Scenarios | Scenario node detail |
| `GET` | `/api/badges/` | Badges | Full badge catalogue |
| `GET` | `/api/badges/{id}` | Badges | Single badge detail |

---

## Security Model

| Layer | Implementation |
|---|---|
| **Passwords** | bcrypt via passlib — intentionally slow, timing-attack safe. Dummy verify on unknown email prevents user enumeration. |
| **Access Token** | JWT HS256 · 30-min expiry · Zustand memory only — **never written to localStorage or sessionStorage** |
| **Refresh Token** | JWT · 7-day expiry · httpOnly cookie (JS cannot read) · SHA-256 hashed before DB storage |
| **Token Rotation** | Each `/auth/refresh` revokes the old token and issues a new pair atomically |
| **Reuse Detection** | Revoked token replayed → **all tokens for that user wiped immediately** (prevents replay attacks) |
| **Ownership Guard** | Every child route checks `child.parent_id == current_user.id` in `Depends()`. Returns 404 for both "not found" and "wrong owner" |
| **Rate Limiting** | 10 logins/min, 5 registrations/min per client IP. In-memory sliding window. Returns 429 with `Retry-After` header |
| **Size Limiting** | Content-Length checked before body parsing. Max 1 MB. Returns 413 with clear error message |
| **Input Sanitisation** | Pydantic v2 validators: email regex, password complexity (min 8 chars, mixed case, digit), age 4–17, name length. Regex blocks `< > " ' % ; ( ) &` in text fields |

---

## Running Tests

```bash
cd skilio-backend

# Activate your virtual environment first
pip install -r requirements.txt

pytest tests/ -v
```

The test suite covers authentication flows including registration, login, token refresh, logout, and invalid credential handling.

---

## Architecture Overview

Skilio follows a clean **three-tier architecture** where every layer has a single responsibility:

```
Browser (React + TypeScript)
    │  Zustand auth store · React Query · React Router v6 · Axios + 401 interceptor
    ▼
Proxy (Vite dev / nginx prod)
    │  /api/* → FastAPI:8000 · Static assets · SPA fallback (try_files)
    ▼
FastAPI (Python 3.11 + uvicorn)
    │  7 routers · 27 endpoints · CORS · Pydantic v2 validation · Depends injection
    │  Rate limiting · Size limits · Request ID middleware · Slow-request logging
    ▼
SQLAlchemy ORM 2.0 + Alembic
    │  13 entities · Mapped[] type annotations · Relationships · Migrations
    ▼
Database
    SQLite (default, zero config) / MySQL / PostgreSQL
    Switched via DATABASE_URL — no code changes required
```

---

## Team

| Name | Role |
|---|---|
| **Raneem** | Co-Founder · Product Architect · Chief Technical Lead |
| **Bochra** | Co-Founder · Backend Contributor · Operations & Presentation Lead |
| **Imed** | Backend Engineer — API & Validation |
| **Mazid** | Data Engineer — Database & Entity Design |
| **Mansour** | Documentation & GitHub Manager |

---

## Stats

| Metric | Count |
|---|---|
| Database entities | 13 |
| API endpoints | 27 |
| API routers | 7 |
| Story worlds | 3 |
| Lessons | 6 |
| Badges | 5 |
| Target age range | 4–17 |

---

*Built with ❤️ for child safety education.*
