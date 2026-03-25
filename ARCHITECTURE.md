# Skilio — Architecture Blueprint

> Scenario-Based Life Skills Learning Platform for Children  
> *For children aged 4–17*

| 12 Entities | 24 API Routes | 6 Routers | 3 Worlds | 6 Lessons | 5 Badges |
|:-----------:|:-------------:|:---------:|:--------:|:---------:|:--------:|

---

## Technology Stack

| Backend | Frontend | Language | ORM |
|---|---|---|---|
| FastAPI 0.111 | React 18 + Vite | TypeScript 5 | SQLAlchemy 2.0 |
| SQLite / MySQL | JWT + bcrypt | TanStack Query v5 | Zustand + Router |

---

> **Why Skilio? — The Academic Motivation**
>
> Traditional child safety education is passive — children memorise rules but never practice decisions.
>
> Skilio replaces this with a scenario engine: a DAG where children navigate realistic situations and see consequences.
>
> Every choice is stored in an audit trail so parents can review exactly how their child reasons under pressure.

---

## 1 · System Architecture

Skilio follows a clean three-tier architecture. Every layer has a single responsibility and communicates only with its neighbours.

### 1.1 Layer Overview

| Layer | Technology | Responsibility |
|---|---|---|
| **Browser** | React 18 + TypeScript | Zustand auth store · React Query · React Router v6 · Axios + 401 interceptor |
| **Proxy** | Vite dev / nginx prod | `/api/*` → FastAPI:8000 · Static assets · SPA fallback (try_files) |
| **FastAPI** | Python 3.11 + uvicorn | 6 routers · 24 endpoints · CORS · Pydantic v2 validation · Depends injection · Rate limiting · Size limits |
| **SQLAlchemy** | ORM 2.0 + Alembic | 12 entities · Mapped[] type annotations · Relationships · Version-controlled migrations |
| **Database** | SQLite / MySQL / PG | Switched via `DATABASE_URL` env var · connect_args auto-adapted per driver · zero config default |

### 1.2 Database Configuration

> **`DATABASE_URL` controls everything — no code changes needed to switch**

```
# SQLite (default, zero config):
sqlite:///./skilio.db

# MySQL:
mysql+pymysql://user:pass@localhost:3306/skilio_db

# PostgreSQL:
postgresql://user:pass@localhost:5432/skilio_db
```

The engine is configured differently per driver:

- **SQLite:** `check_same_thread=False` — required for FastAPI's threaded request model
- **MySQL / PostgreSQL:** `connect_timeout=5` — server fails fast if database is unreachable
- **Both:** `pool_pre_ping=True` — validates connections before use, prevents stale-connection errors

### 1.3 Security Architecture

| Layer | Implementation |
|---|---|
| **Passwords** | bcrypt via passlib — intentionally slow, timing-attack safe. Dummy verify on unknown email prevents user enumeration. |
| **Access Token** | JWT HS256 · 30-min expiry · Zustand memory ONLY — never written to localStorage or sessionStorage. |
| **Refresh Token** | JWT · 7-day expiry · httpOnly cookie (JS cannot read) · SHA-256 hashed before DB storage. |
| **Token Rotation** | Each `/auth/refresh` revokes the old token and issues a new pair. Atomic — flush old before insert new. |
| **Reuse Detection** | Revoked token presented again → ALL tokens for that user wiped immediately. Prevents replay attacks. |
| **Ownership Guard** | Every child route: `child.parent_id == current_user.id` checked in FastAPI `Depends()`. Returns 404 for both 'not found' and 'wrong owner'. |
| **Rate Limiting** | 10 logins/min, 5 registrations/min per client IP. In-memory with 60-second sliding window. Returns 429 with `Retry-After` header. |
| **Size Limiting** | Content-Length checked before body parsing. Max 1 MB. Returns 413 with clear error message. |
| **Input Sanitisation** | Pydantic v2 validators: email regex, password complexity, age 4–17, name length. Regex blocks `< > " ' % ; ( ) &` in text fields. |

---

## 2 · Data Model — 12 Entities

All entities use SQLAlchemy 2.0's `Mapped[]` type annotations, catching type errors at development time rather than runtime.

### 2.1 Entity Relationship Overview

```
User ──< Child ──< ScenarioAttempt ──< ScenarioAttemptChoice
           │               │                     │
           │       ScenarioChoice ───────────────┘
           │
           └─< RefreshToken

SkillModule ──< Lesson ──< ScenarioNode
                                │
                         next_node_id ──► ScenarioNode   ← SELF-REFERENTIAL DAG

Child ──< Progress    (one row per child per module)
Child ──< BadgeAward ──► Badge
```

> **Key Advanced Relationships**
>
> - **Self-referential DAG:** `ScenarioNode → ScenarioChoice.next_node_id → ScenarioNode`
> - **Audit trail entity:** `ScenarioAttemptChoice` records every individual decision with timestamp
> - **Composite unique:** `Progress(child_id, module_id)` — one progress row per child per world
> - **Soft delete:** `Child.is_active` — data retained, 404 returned for inactive records

### 2.2 All 12 Entity Tables

#### `users`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment primary key |
| `email` | VARCHAR(255) UNIQUE | Indexed, lowercased on write |
| `full_name` | VARCHAR(100) | Min 2 chars, sanitised input |
| `hashed_password` | VARCHAR(255) | bcrypt hash — never stored plain |
| `is_active` | BOOLEAN | Soft-delete flag |
| `created_at` / `updated_at` | DATETIME | Server-managed timestamps |

#### `children`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `parent_id` | INTEGER FK → users | CASCADE DELETE, indexed |
| `display_name` | VARCHAR(50) | Min 1 char, sanitised |
| `age` | INTEGER | 4–17 enforced by Pydantic |
| `total_xp` | INTEGER | Aggregate XP, updated after each lesson |
| `is_active` | BOOLEAN | Soft delete |

#### `skill_modules`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `title` | VARCHAR(100) | e.g. Outer Space |
| `description` | TEXT | Full lesson-list description |
| `age_min` / `age_max` | INTEGER | Used for `?age=` query filter |
| `is_published` | BOOLEAN | Only published modules shown |
| `order_index` | INTEGER | Controls display order |

#### `lessons`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `module_id` | INTEGER FK → skill_modules | CASCADE DELETE |
| `entry_node_id` | INTEGER FK → scenario_nodes | SET NULL, use_alter (circular FK) |
| `title` | VARCHAR(150) | Lesson title |
| `xp_reward` | INTEGER | XP for correct-path completion |
| `order_index` | INTEGER | Order within module |

#### `scenario_nodes`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `lesson_id` | INTEGER FK → lessons | CASCADE DELETE, indexed |
| `content_text` | TEXT | NPC dialogue / story text |
| `node_type` | ENUM | `START` \| `BRANCH` \| `END` |
| `is_correct_path` | BOOLEAN | True = full XP on reach |

#### `scenario_choices`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `node_id` | INTEGER FK → scenario_nodes | CASCADE DELETE |
| `next_node_id` | INTEGER FK → scenario_nodes | ★ SELF-REFERENTIAL — SET NULL |
| `choice_text` | VARCHAR(500) | Button label shown to child |
| `is_safe_choice` | BOOLEAN | Used for badge trigger counting |
| `feedback_text` | VARCHAR(500) | Toast message shown after choice |

#### `scenario_attempts`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `child_id` | INTEGER FK → children | CASCADE DELETE, indexed |
| `lesson_id` | INTEGER FK → lessons | CASCADE DELETE |
| `current_node_id` | INTEGER FK → scenario_nodes | RESTRICT — prevents orphaned state |
| `status` | ENUM | `IN_PROGRESS` \| `COMPLETED` \| `ABANDONED` |
| `xp_earned` | INTEGER | Set on completion based on path taken |
| `completed_at` | DATETIME | NULL until attempt finishes |

#### `scenario_attempt_choices`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `attempt_id` | INTEGER FK → scenario_attempts | CASCADE DELETE, indexed |
| `node_id` | INTEGER FK → scenario_nodes | RESTRICT — audit trail |
| `choice_id` | INTEGER FK → scenario_choices | RESTRICT — audit trail |
| `chosen_at` | DATETIME | Server default NOW() — immutable audit timestamp |

#### `progress`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `child_id` | INTEGER FK → children | CASCADE, UNIQUE with module_id |
| `module_id` | INTEGER FK → skill_modules | CASCADE |
| `lessons_completed` | INTEGER | Recalculated after every attempt |
| `total_lessons` | INTEGER | Cached module lesson count |
| `last_activity_at` | DATETIME | Auto-updated on write |

#### `badges`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `name` | VARCHAR(100) UNIQUE | e.g. Safety Explorer |
| `trigger_type` | ENUM | `first_lesson` \| `lesson_count` \| `module_complete` \| `xp_milestone` \| `safe_choices` |
| `trigger_value` | INTEGER | Threshold for the trigger type |
| `xp_bonus` | INTEGER | Extra XP awarded when badge earned |
| `is_active` | BOOLEAN | Toggle badges without deleting |

#### `badge_awards`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `child_id` | INTEGER FK → children | CASCADE, indexed |
| `badge_id` | INTEGER FK → badges | CASCADE |
| `awarded_at` | DATETIME | Server default NOW() |
| `trigger_context` | JSON | Audit data: lesson_id, attempt_id, etc. |

#### `refresh_tokens`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `user_id` | INTEGER FK → users | CASCADE DELETE, indexed |
| `token_hash` | VARCHAR(64) UNIQUE | SHA-256 of raw JWT |
| `expires_at` | DATETIME | Checked on every refresh |
| `revoked` | BOOLEAN | True = used or force-logged-out |

---

## 3 · API Reference — 24 Endpoints

Auto-generated Swagger UI available at **`http://localhost:8000/docs`** — all endpoints testable without setup.

### Auth — `/api/auth`

| Method | Path | Description |
|---|---|---|
| `POST` | `/register` | Create account · email regex + password complexity (Pydantic) · rate-limited 5/min |
| `POST` | `/login` | JWT access token + httpOnly refresh cookie · bcrypt verify · rate-limited 10/min |
| `POST` | `/refresh` | Single-use rotation · replay → all tokens wiped · new pair issued atomically |
| `POST` | `/logout` | Revoke refresh token + clear httpOnly cookie |
| `GET` | `/me` | Current authenticated parent profile |

### Children — `/api/children`

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | List parent's children — JWT-scoped, no cross-access |
| `POST` | `/` | Create child · age 4–17 enforced server-side by Pydantic Field |
| `GET` | `/{id}` | Child detail — ownership guard via `get_owned_child` Depends() |
| `PUT` | `/{id}` | Update display_name or age — partial updates, all fields optional |
| `DELETE` | `/{id}` | Soft delete — `is_active=False`, data retained for audit |
| `GET` | `/{id}/summary` | Dashboard: total XP + module progress + badges in one request |
| `GET` | `/{id}/progress` | Per-module completion percentages and last activity timestamps |
| `GET` | `/{id}/badges` | Earned badges with `trigger_context` JSON audit log |
| `GET` | `/{id}/attempts` | Last 20 scenario attempts ordered by date |

### Scenarios — `/api/scenarios`

| Method | Path | Description |
|---|---|---|
| `POST` | `/attempts` | Start or RESUME — idempotent, returns existing if `in_progress` |
| `POST` | `/attempts/{id}/choose` | Submit choice → advance DAG → next node + feedback toast |
| `GET` | `/attempts/{id}` | Current state for page-refresh resume |
| `GET` | `/attempts/{id}/history` | Full choice audit trail with node content + timestamps |
| `GET` | `/nodes/{id}` | Node with choices — `next_node_id` intentionally hidden from client |

### Modules, Lessons & Badges

| Method | Path | Description |
|---|---|---|
| `GET` | `/modules/` | Published worlds with optional `?age=` filter |
| `GET` | `/modules/{id}` | World with ordered lesson list and `entry_node_id` |
| `GET` | `/lessons/{id}` | Lesson detail including `entry_node_id` to start scenario |
| `GET` | `/badges/` | All active badges — shows locked/unlocked state |
| `GET` | `/badges/{id}` | Badge detail with trigger type and XP bonus |

---

## 4 · Frontend Architecture

### 4.1 Component Structure

| File / Directory | Purpose |
|---|---|
| `main.tsx` | `boot()` runs before first render: calls `authApi.refresh()` → sets auth or clears. Mounts React only after auth state is known. |
| `router.tsx` | `createBrowserRouter` with `ProtectedRoute` and `PublicRoute`. Nested layout via `AppShell`. |
| `AppShell` | Sidebar (desktop nav) + MobileNav (fixed bottom) + `<Outlet/>` for page content. |
| `store/authStore.ts` | Zustand: user profile + JWT access token in memory. `isLoading=true` until `boot()` resolves. |
| `store/scenarioStore.ts` | Zustand: live game state — `currentNode`, `attempt`, `pendingFeedback`, `isAdvancing`. |
| `api/client.ts` | Axios instance with 401 interceptor. On 401: queues requests, refreshes token, replays all queued. |
| `hooks/useAuth.ts` | `useLogin`, `useRegister`, `useLogout` — React Query mutations with navigation side effects. |
| `hooks/useChildren.ts` | `useChildren`, `useChild`, `useChildSummary`, `useCreateChild`, `useUpdateChild`, `useDeleteChild`. |
| `pages/auth/` | Login (split-panel layout), Register — react-hook-form with client-side validation. |
| `pages/parent/` | Dashboard (child XP cards), ManageChildren (CRUD form), ChildDetail (progress + badges). |
| `pages/learn/` | ModuleBrowser (world cards), LessonList (start/resume), ScenarioPlayer (DAG traversal). |
| `styles/globals.css` | Skilio brand: `--pu:#7c3aed`, `--nav:#0d0a1a`, Fredoka One + Nunito. Kids animations. |

> **State Management — Two-Store Pattern**
>
> - **authStore (Zustand):** JWT token in memory only. Never written to localStorage or sessionStorage.
> - **scenarioStore (Zustand):** live game state reset on exit. Decoupled from server state.
> - **React Query:** all server data. Auto-stale, background refetch, optimistic updates.
> - **Axios 401 interceptor:** silent token refresh. Queues concurrent requests during refresh.

---

## 5 · Quickstart & Deployment

Works with **zero configuration** using SQLite. No MySQL, no Docker, no `.env` file needed to run.

### Step 1 — Install Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows):
.venv\Scripts\activate

# Activate (Mac / Linux):
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2 — Create Tables (SQLite — zero config)

```bash
# No .env file needed — SQLite is the default database
alembic upgrade head

# Seed demo data (3 worlds, 6 lessons, 5 badges, demo parent + 2 children)
python scripts/seed.py

# Creates: backend/skilio.db
```

### Step 3 — Start API Server

```bash
uvicorn app.main:app --reload --port 8000
# Swagger UI:    http://localhost:8000/docs
# Health check:  http://localhost:8000/health
# ReDoc:         http://localhost:8000/redoc
```

### Step 4 — Start Frontend

```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
# Vite proxies /api/* to localhost:8000 automatically
```

### Step 5 — Login with Demo Account

| | |
|---|---|
| **Email** | `demo@skilio.com` |
| **Password** | `Demo1234!` |
| **Children** | Elif (age 8) · Kerem (age 11) |
| **Worlds** | 🌌 Outer Space · 🌊 The Deep Sea · 🌲 Enchanted Forest |
| **Badges** | First Step · Safety Explorer · World Champion · XP Pioneer · Safe Choice Champion |

> **Switch to MySQL**
>
> Create `backend/.env` with:
> ```
> DATABASE_URL=mysql+pymysql://skilio:skiliopass@localhost:3306/skilio_db
> ```
> No code changes — the engine adapts automatically to the driver.

### Running Tests

```bash
cd backend
pytest tests/ -v
# Tests use in-memory SQLite — no external services needed
# Covers: registration, login, token validation, ownership guards, rate limits
```

---

## 6 · Project File Structure

```
skilio/
├── backend/
│   ├── app/
│   │   ├── api/              # Route handlers — HTTP only, delegates to services
│   │   │   ├── auth.py       # register, login, refresh, logout, me + rate limiting
│   │   │   ├── children.py   # CRUD + 4 sub-resource routes
│   │   │   ├── modules.py    # world list + detail
│   │   │   ├── lessons.py    # lesson detail
│   │   │   ├── scenarios.py  # DAG engine endpoints
│   │   │   └── badges.py     # badge catalogue
│   │   ├── core/
│   │   │   ├── config.py     # Pydantic BaseSettings — SQLite default, no crash without .env
│   │   │   ├── database.py   # Engine auto-adapted: SQLite vs MySQL vs PostgreSQL
│   │   │   ├── security.py   # bcrypt, JWT create/decode, timing-safe
│   │   │   └── dependencies.py  # get_db, auth guards, ownership guards
│   │   ├── models/           # 12 SQLAlchemy entities with Mapped[] type annotations
│   │   ├── schemas/          # Pydantic v2 schemas with validators + input sanitisation
│   │   └── services/         # Business logic: scenario DAG, XP, badge checks, progress
│   ├── alembic/              # Version-controlled schema migrations
│   ├── scripts/seed.py       # Demo data — 3 worlds, 6 full scenarios, 5 badges
│   ├── screenshots/          # 3 SVG screenshots for GitHub README
│   ├── tests/                # pytest suite — in-memory SQLite, no external deps
│   ├── requirements.txt
│   └── .env.example          # SQLite default shown first, MySQL optional
│
└── frontend/
    ├── src/
    │   ├── api/              # Axios + silent 401 refresh interceptor
    │   ├── components/       # AppShell, Sidebar, MobileNav, UI kit
    │   ├── hooks/            # React Query wrappers for all API calls
    │   ├── pages/            # 8 pages: auth, parent portal, learning space
    │   ├── store/            # authStore + scenarioStore (Zustand)
    │   └── styles/globals.css  # Skilio brand system
    └── vite.config.ts        # /api proxy → localhost:8000
```
