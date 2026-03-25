# Skilio — Architecture Blueprint

> Scenario-Based Life Skills Learning Platform for Children  
> *For children aged 4–17*

| 13 Entities | 27 API Endpoints | 7 Routers | 3 Worlds | 6 Lessons | 5 Badges |
|:-----------:|:----------------:|:---------:|:--------:|:---------:|:--------:|

> ⚠️ This document was reconstructed directly from the source code. All entity schemas, route counts, and implementation details reflect the actual codebase.

---

## Technology Stack

| Backend | Frontend | Language | ORM |
|---|---|---|---|
| FastAPI 0.111 | React 18 + Vite 5 | TypeScript 5 | SQLAlchemy 2.0 |
| SQLite / MySQL / PostgreSQL | JWT + bcrypt | TanStack Query v5 | Zustand 4 + React Router v6 |

---

## Why Skilio?

Traditional child safety education is passive — children memorise rules but never practice decisions.

Skilio replaces this with a **scenario engine**: a directed acyclic graph (DAG) where children navigate realistic situations and see consequences. Every choice is stored in an audit trail so parents can review exactly how their child reasons under pressure.

---

## 1 · System Architecture

Skilio follows a clean three-tier architecture. Every layer has a single responsibility and communicates only with its neighbours.

### 1.1 Layer Overview

| Layer | Technology | Responsibility |
|---|---|---|
| **Browser** | React 18 + TypeScript | Zustand auth store · React Query · React Router v6 · Axios + 401 interceptor |
| **Proxy** | Vite dev / nginx prod | `/api/*` → FastAPI:8000 · Static assets · SPA fallback (`try_files`) |
| **FastAPI** | Python 3.11 + uvicorn | 7 routers · 27 endpoints · CORS · Pydantic v2 validation · `Depends` injection · Rate limiting · Size limits |
| **SQLAlchemy** | ORM 2.0 + Alembic | 13 entities · `Mapped[]` type annotations · Relationships · Version-controlled migrations |
| **Database** | SQLite / MySQL / PostgreSQL | Switched via `DATABASE_URL` env var · `connect_args` auto-adapted per driver · zero config default |

### 1.2 Database Configuration

`DATABASE_URL` controls everything — no code changes needed to switch databases:

```bash
# SQLite (default, zero config):
DATABASE_URL=sqlite:///./skilio.db

# MySQL:
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/skilio_db

# PostgreSQL:
DATABASE_URL=postgresql://user:pass@localhost:5432/skilio_db
```

The engine is configured differently per driver (from `app/core/database.py`):

- **SQLite:** `check_same_thread=False` — required for FastAPI's threaded request model
- **MySQL / PostgreSQL:** `connect_timeout=5` — server fails fast if database is unreachable
- **Both:** `pool_pre_ping=True` — validates connections before use, prevents stale-connection errors

### 1.3 Security Architecture

| Layer | Implementation |
|---|---|
| **Passwords** | bcrypt via passlib — intentionally slow, timing-attack safe. Dummy verify on unknown email prevents user enumeration. |
| **Access Token** | JWT HS256 · 30-min expiry · Zustand memory ONLY — never written to localStorage or sessionStorage (enforced in `authStore.ts`). |
| **Refresh Token** | JWT · 7-day expiry · httpOnly cookie named `skilio_refresh` (JS cannot read) · SHA-256 hashed before DB storage. |
| **Token Rotation** | Each `POST /auth/refresh` revokes the old token and issues a new pair. Atomic — `db.flush()` old before inserting new. |
| **Reuse Detection** | Revoked token presented again → ALL tokens for that user wiped immediately (`UPDATE refresh_tokens SET revoked=True WHERE user_id=...`). Prevents replay attacks. |
| **Ownership Guard** | Every child route: `child.parent_id == current_user.id` checked in `get_owned_child` `Depends()`. Returns 404 for both "not found" and "wrong owner" (prevents enumeration). |
| **Rate Limiting** | 10 logins/min, 5 registrations/min per client IP. In-memory sliding window (`defaultdict(list)` with thread `Lock`). Returns 429 with `Retry-After: 60` header. |
| **Size Limiting** | `Content-Length` checked before body parsing. Max 1 MB (`1_048_576` bytes). Returns 413 with clear error message. |
| **Input Sanitisation** | Pydantic v2 validators: email regex, password complexity, age 4–17, name length limits. |
| **401 Handling** | Axios response interceptor calls `clearAuth()` and redirects to `/login` on any 401 response. |

---

## 2 · Data Model — 13 Entities

All entities use SQLAlchemy 2.0's `Mapped[]` type annotations, catching type errors at development time.

### 2.1 Entity Relationship Overview

```
User ──< Child ──< ScenarioAttempt ──< ScenarioAttemptChoice
  │          │              │                    │
  │          │       ScenarioChoice ─────────────┘
  │          │
  │          ├──< BadgeAward ──> Badge ──< ModuleBadge ──> SkillModule
  │          │                                                  │
  │          ├──< Progress                          SkillModule ──< Lesson
  │          │                                                        │
  └──< RefreshToken                                         Lesson ──< ScenarioNode
                                                                           │
                                                       next_node_id ──► ScenarioNode
                                                                   ← SELF-REFERENTIAL DAG
```

**Key advanced relationships:**

- **Self-referential DAG** — `ScenarioNode → ScenarioChoice.next_node_id → ScenarioNode`. `next_node_id=NULL` signals a terminal choice (scenario ends).
- **Circular FK** — `Lesson.entry_node_id → scenario_nodes.id` AND `ScenarioNode.lesson_id → lessons.id`. Solved with `use_alter=True` + `post_update=True` in SQLAlchemy.
- **Many-to-many** — `SkillModule ↔ Badge` via `ModuleBadge` association table (13th entity).
- **Audit trail** — `ScenarioAttemptChoice` records every individual decision with an immutable server-side timestamp.
- **Composite unique** — `Progress(child_id, module_id)` — one progress row per child per world.
- **Soft delete** — `Child.is_active` and `User.is_active` — data retained, 404 returned for inactive records.

### 2.2 All 13 Entity Tables

#### `users`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `email` | VARCHAR(255) UNIQUE | Indexed, unique |
| `full_name` | VARCHAR(100) | Min 2 chars |
| `hashed_password` | VARCHAR(255) | bcrypt hash — never stored plain |
| `is_active` | BOOLEAN | Soft-delete flag |
| `created_at` / `updated_at` | DATETIME | Server-managed via `TimestampMixin` |

#### `children`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `parent_id` | INTEGER FK → users | CASCADE DELETE, indexed |
| `display_name` | VARCHAR(50) | Min 1 char |
| `age` | INTEGER | 4–17 enforced by Pydantic |
| `avatar_url` | VARCHAR(500) | Nullable — optional child avatar |
| `total_xp` | INTEGER | Aggregate XP, updated after each lesson |
| `is_active` | BOOLEAN | Soft delete |
| `created_at` / `updated_at` | DATETIME | `TimestampMixin` |

#### `skill_modules`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `title` | VARCHAR(100) | e.g. "Outer Space" |
| `description` | TEXT | Full module description |
| `thumbnail_url` | VARCHAR(500) | Nullable — module card image |
| `age_min` / `age_max` | INTEGER | Used for `?age=` query filter |
| `is_published` | BOOLEAN | Only published modules shown |
| `order_index` | INTEGER | Controls display order |
| `created_at` / `updated_at` | DATETIME | `TimestampMixin` |

#### `lessons`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `module_id` | INTEGER FK → skill_modules | CASCADE DELETE, indexed |
| `entry_node_id` | INTEGER FK → scenario_nodes | `use_alter=True` + `post_update=True` (circular FK), SET NULL |
| `title` | VARCHAR(150) | Lesson title |
| `description` | TEXT | Nullable — lesson overview text |
| `xp_reward` | INTEGER | XP for scenario completion (default 50) |
| `order_index` | INTEGER | Order within module |
| `created_at` / `updated_at` | DATETIME | `TimestampMixin` |

#### `scenario_nodes`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `lesson_id` | INTEGER FK → lessons | CASCADE DELETE, indexed |
| `content_text` | TEXT | NPC dialogue / story text |
| `image_url` | VARCHAR(500) | Nullable — optional illustration for this story beat |
| `node_type` | ENUM | `start` \| `branch` \| `end` |
| `is_correct_path` | BOOLEAN | True = full XP awarded on reaching this node |
| `created_at` / `updated_at` | DATETIME | `TimestampMixin` |

#### `scenario_choices`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `node_id` | INTEGER FK → scenario_nodes | CASCADE DELETE, indexed |
| `next_node_id` | INTEGER FK → scenario_nodes | ★ SELF-REFERENTIAL — SET NULL (NULL = scenario ends) |
| `choice_text` | VARCHAR(500) | Button label shown to child |
| `is_safe_choice` | BOOLEAN | Used for badge trigger counting |
| `feedback_text` | VARCHAR(500) | Nullable — toast message shown after choice |
| `order_index` | INTEGER | Display order among sibling choices (default 0) |

#### `scenario_attempts`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `child_id` | INTEGER FK → children | CASCADE DELETE, indexed |
| `lesson_id` | INTEGER FK → lessons | CASCADE DELETE, indexed |
| `current_node_id` | INTEGER FK → scenario_nodes | RESTRICT — prevents orphaned state |
| `status` | ENUM | `in_progress` \| `completed` \| `abandoned` |
| `xp_earned` | INTEGER | Set on completion based on path taken |
| `completed_at` | DATETIME | Nullable — NULL until attempt finishes |
| `created_at` / `updated_at` | DATETIME | `TimestampMixin` |

#### `scenario_attempt_choices`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `attempt_id` | INTEGER FK → scenario_attempts | CASCADE DELETE, indexed |
| `node_id` | INTEGER FK → scenario_nodes | RESTRICT — immutable audit trail |
| `choice_id` | INTEGER FK → scenario_choices | RESTRICT — immutable audit trail |
| `chosen_at` | DATETIME | `server_default=func.now()` — immutable audit timestamp |

#### `progress`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `child_id` | INTEGER FK → children | CASCADE, UNIQUE with module_id |
| `module_id` | INTEGER FK → skill_modules | CASCADE |
| `lessons_completed` | INTEGER | Recalculated after every attempt |
| `total_lessons` | INTEGER | Cached module lesson count (avoids re-aggregation) |
| `last_activity_at` | DATETIME | `server_default` + `onupdate=func.now()` |

Includes a `completion_percentage` computed property (0.0–100.0).

#### `badges`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `name` | VARCHAR(100) UNIQUE | e.g. "Safety Explorer" |
| `description` | TEXT | Badge description shown to user |
| `image_url` | VARCHAR(500) | Nullable — badge icon |
| `trigger_type` | ENUM | `first_lesson` \| `lesson_count` \| `module_complete` \| `xp_milestone` \| `safe_choices` |
| `trigger_value` | INTEGER | Threshold for the trigger (e.g. 5 for "complete 5 lessons") |
| `xp_bonus` | INTEGER | Extra XP awarded alongside the badge |
| `is_active` | BOOLEAN | Toggle without deleting |
| `created_at` / `updated_at` | DATETIME | `TimestampMixin` |

#### `badge_awards`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `child_id` | INTEGER FK → children | CASCADE, indexed |
| `badge_id` | INTEGER FK → badges | CASCADE, indexed |
| `awarded_at` | DATETIME | `server_default=func.now()` |
| `trigger_context` | JSON | Nullable — audit data: `{lesson_id, attempt_id, trigger}` |

#### `module_badges` *(association table — 13th entity)*

| Column | Type | Notes |
|---|---|---|
| `module_id` | INTEGER FK → skill_modules (PK) | CASCADE DELETE |
| `badge_id` | INTEGER FK → badges (PK) | CASCADE DELETE |
| `is_completion_badge` | BOOLEAN | True = requires completing ALL lessons in the module |

Links `Badge` ↔ `SkillModule` many-to-many. A badge can belong to multiple modules; a module can have multiple badges.

#### `refresh_tokens`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `user_id` | INTEGER FK → users | CASCADE DELETE · composite index with `revoked` |
| `token_hash` | VARCHAR(64) UNIQUE | SHA-256 hex digest of raw JWT (always 64 chars) |
| `expires_at` | DATETIME | Checked on every refresh request |
| `revoked` | BOOLEAN | True = used or force-logged-out |
| `created_at` | DATETIME | `server_default=func.now()` |

---

## 3 · API Reference — 27 Endpoints

Full interactive docs at **`http://localhost:8000/docs`** (Swagger UI) and **`http://localhost:8000/redoc`** (ReDoc).

### Auth — `/api/auth` (5 endpoints)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create parent account · email + password validation · rate-limited 5/min per IP |
| `POST` | `/api/auth/login` | JWT access token + `skilio_refresh` httpOnly cookie · bcrypt verify · rate-limited 10/min per IP |
| `POST` | `/api/auth/refresh` | Single-use rotation · replay → all user tokens wiped · new pair issued atomically |
| `POST` | `/api/auth/logout` | Revoke refresh token + `response.delete_cookie()` |
| `GET` | `/api/auth/me` | Current authenticated parent profile |

### Users — `/api/users` (3 endpoints)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/users/me` | Read own profile |
| `PUT` | `/api/users/me` | Update `full_name` only — email change out of scope for MVP |
| `DELETE` | `/api/users/me` | Soft-deactivate account (`is_active=False`) — JWT still decodes but `require_active_user` rejects with 403 |

### Children — `/api/children` (9 endpoints)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/children/` | List parent's own children — JWT-scoped |
| `POST` | `/api/children/` | Create child · age 4–17 enforced by Pydantic |
| `GET` | `/api/children/{child_id}` | Child detail — ownership via `get_owned_child` `Depends()` |
| `PUT` | `/api/children/{child_id}` | Update `display_name`, `age`, `avatar_url` — all optional |
| `DELETE` | `/api/children/{child_id}` | Soft-delete — `is_active=False`, history preserved |
| `GET` | `/api/children/{child_id}/progress` | Per-module completion percentages |
| `GET` | `/api/children/{child_id}/badges` | Earned badges with `trigger_context` JSON |
| `GET` | `/api/children/{child_id}/attempts` | Last 20 scenario attempts ordered by date |
| `GET` | `/api/children/{child_id}/summary` | Dashboard: total XP + module progress + badges + recent attempt count |

### Scenarios — `/api/scenarios` (5 endpoints)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/scenarios/attempts` | Start or resume — idempotent, returns existing `in_progress` attempt |
| `GET` | `/api/scenarios/attempts/{attempt_id}` | Current attempt state + current node (for page-refresh resume) |
| `POST` | `/api/scenarios/attempts/{attempt_id}/choose` | Submit choice → advance DAG → return next node + feedback + badge IDs |
| `GET` | `/api/scenarios/attempts/{attempt_id}/history` | Full ordered choice audit trail with node content preview |
| `GET` | `/api/scenarios/nodes/{node_id}` | Node with choices — `next_node_id` intentionally excluded from response |

### Modules — `/api/modules` (2 endpoints)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/modules/` | All published modules · optional `?age=` filter (4–17) |
| `GET` | `/api/modules/{module_id}` | Module with ordered lesson list |

### Lessons — `/api/lessons` (1 endpoint)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/lessons/{lesson_id}` | Lesson detail including `entry_node_id` |

### Badges — `/api/badges` (2 endpoints)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/badges/` | All active badges |
| `GET` | `/api/badges/{badge_id}` | Single badge detail |

### Health (1 endpoint)

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Returns `{status, app, version, database}` — database type auto-detected from `DATABASE_URL` |

---

## 4 · Frontend Architecture

### 4.1 Routing Structure (`src/router.tsx`)

```
/                               → redirect to /dashboard
/login                          → LoginPage        (PublicRoute)
/register                       → RegisterPage     (PublicRoute)

/dashboard                      → DashboardPage        (ProtectedRoute > AppShell)
/children                       → ManageChildrenPage   (ProtectedRoute > AppShell)
/children/:childId              → ChildDetailPage      (ProtectedRoute > AppShell)
/learn                          → ModuleBrowserPage    (ProtectedRoute > AppShell)
/learn/:moduleId                → LessonListPage       (ProtectedRoute > AppShell)
/learn/:moduleId/:lessonId/play → ScenarioPlayerPage   (ProtectedRoute > AppShell)
*                               → redirect to /dashboard
```

### 4.2 Component & File Structure

| File / Directory | Purpose |
|---|---|
| `src/main.tsx` | `QueryClientProvider` wraps `RouterProvider`. React Query config: `staleTime: 60s`, `retry: 1`, `refetchOnWindowFocus: false`. |
| `src/router.tsx` | `createBrowserRouter` with `ProtectedRoute` and `PublicRoute` guards. Nested layout via `AppShell`. |
| `src/components/layout/AppShell.tsx` | Sidebar (desktop) + MobileNav (fixed bottom bar) + `<Outlet/>`. |
| `src/store/authStore.ts` | Zustand: `user`, `token` (memory only), `isLoading`. Actions: `setAuth`, `clearAuth`, `setUser`, `setLoading`. |
| `src/store/scenarioStore.ts` | Zustand: `attempt`, `currentNode`, `pendingFeedback`, `newlyAwardedBadgeIds`, `isAdvancing`. Reset on exit via `resetScenario()`. |
| `src/api/client.ts` | Axios instance. Request interceptor injects `Authorization: Bearer <token>`. Response interceptor on 401: calls `clearAuth()` + `window.location.href = '/login'`. |
| `src/hooks/useAuth.ts` | `useLogin`, `useRegister`, `useLogout` — React Query mutations. |
| `src/hooks/useChildren.ts` | `useChildren`, `useChild`, `useChildSummary`, `useCreateChild`, `useUpdateChild`, `useDeleteChild`. |
| `src/hooks/useModules.ts` | `useModules`, `useModule` hooks. |
| `src/hooks/useScenario.ts` | `useStartAttempt`, `useSubmitChoice` hooks. |
| `src/pages/auth/` | `Login.tsx` (split-panel layout), `Register.tsx`. |
| `src/pages/parent/` | `Dashboard.tsx`, `ManageChildren.tsx`, `ChildDetail.tsx`. |
| `src/pages/learn/` | `ModuleBrowser.tsx`, `LessonList.tsx`, `ScenarioPlayer.tsx`. |
| `src/components/scenario/` | `ChoiceButton.tsx`, `FeedbackToast.tsx`, `CompletionScreen.tsx`. |
| `src/components/ui/` | `Avatar.tsx`, `ProgressBar.tsx`, `XPBar.tsx`, `Spinner.tsx`, `EmptyState.tsx`, `ErrorMessage.tsx`. |
| `src/styles/globals.css` | Skilio brand: `--pu:#7c3aed`, `--nav:#0d0a1a`, Fredoka One + Nunito fonts. |
| `src/types/index.ts` | TypeScript interfaces mirroring all FastAPI/Pydantic response schemas. |
| `src/utils/format.ts` | Shared formatting utilities. |

### 4.3 State Management

| Store | What it holds | Why not React Query |
|---|---|---|
| **`authStore` (Zustand)** | `user`, `token`, `isLoading` | Token must live in memory — never serialized to storage |
| **`scenarioStore` (Zustand)** | Live game state — current node, feedback, newly awarded badge IDs, advancing flag | Changes on every click; needs instant local updates without a server round-trip |
| **React Query** | All server data — children, modules, progress, badges, attempts | Auto-stale, background refetch, cache invalidation on mutations |

---

## 5 · Quickstart & Deployment

Works with **zero configuration** using SQLite. No MySQL, no Docker, no `.env` file needed.

### Step 1 — Install Backend

```bash
cd skilio-backend

python -m venv .venv
source .venv/bin/activate       # Mac/Linux
# .venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

### Step 2 — Run Migrations and Seed

```bash
alembic upgrade head
python scripts/seed.py
# Creates: skilio-backend/skilio.db
```

### Step 3 — Start API Server

```bash
uvicorn app.main:app --reload --port 8000
# Swagger UI:   http://localhost:8000/docs
# ReDoc:        http://localhost:8000/redoc
# Health check: http://localhost:8000/health
```

### Step 4 — Start Frontend

```bash
cd skilio-frontend
npm install
npm run dev
# App: http://localhost:5173
# Vite proxies /api/* → localhost:8000 automatically
```

### Demo Login

| | |
|---|---|
| Email | `demo@skilio.com` |
| Password | `Demo1234!` |
| Children | Elif (age 8) · Kerem (age 11) |
| Worlds | 🌌 Outer Space · 🌊 The Deep Sea · 🌲 Enchanted Forest |

### Switch to MySQL

```env
# skilio-backend/.env
DATABASE_URL=mysql+pymysql://skilio:skiliopass@localhost:3306/skilio_db
```

No code changes — the engine adapts automatically. Use `docker compose up --build` for a full stack.

### Run Tests

```bash
cd skilio-backend
pytest tests/ -v
# In-memory SQLite — no external services needed
```

---

## 6 · Project File Structure

```
skilio/
├── skilio-backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── router.py       # Central aggregator — 7 routers registered here
│   │   │   ├── auth.py         # register, login, refresh, logout, me + rate limiting
│   │   │   ├── users.py        # GET/PUT/DELETE /users/me
│   │   │   ├── children.py     # CRUD + 4 sub-resource routes (9 total)
│   │   │   ├── modules.py      # list + detail (published only, ?age= filter)
│   │   │   ├── lessons.py      # lesson detail
│   │   │   ├── scenarios.py    # DAG engine: start, get, choose, history, node
│   │   │   └── badges.py       # badge catalogue
│   │   ├── core/
│   │   │   ├── config.py       # Pydantic BaseSettings — SQLite default, no crash without .env
│   │   │   ├── database.py     # Engine auto-adapted: SQLite vs MySQL vs PostgreSQL
│   │   │   ├── security.py     # bcrypt, JWT create/decode (access + refresh token types)
│   │   │   └── dependencies.py # get_db, require_active_user, get_owned_child, get_owned_attempt
│   │   ├── models/
│   │   │   ├── base.py         # TimestampMixin (created_at, updated_at)
│   │   │   ├── user.py         # User
│   │   │   ├── child.py        # Child (includes avatar_url)
│   │   │   ├── module.py       # SkillModule (includes thumbnail_url)
│   │   │   ├── lesson.py       # Lesson (circular FK with ScenarioNode via use_alter)
│   │   │   ├── scenario.py     # ScenarioNode (image_url), ScenarioChoice (order_index),
│   │   │   │                   # ScenarioAttempt, ScenarioAttemptChoice
│   │   │   ├── badge.py        # Badge (description + image_url), BadgeAward, ModuleBadge
│   │   │   ├── progress.py     # Progress (with completion_percentage property)
│   │   │   └── token.py        # RefreshToken (SHA-256 hash, composite index)
│   │   ├── schemas/            # Pydantic v2 request/response schemas
│   │   ├── services/           # Business logic: auth, badge, child, progress, scenario
│   │   └── crud/               # DB query helpers: base, crud_user, crud_child, crud_scenario
│   ├── alembic/                # Version-controlled schema migrations
│   ├── scripts/seed.py         # Demo data — 3 worlds, 6 full scenarios, 5 badges
│   ├── tests/                  # pytest suite — in-memory SQLite
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml      # MySQL + backend + frontend full-stack
│   └── .env.example
│
└── skilio-frontend/
    ├── src/
    │   ├── api/                # client.ts (Axios + interceptors), auth.ts, children.ts,
    │   │                       # modules.ts, scenarios.ts
    │   ├── components/
    │   │   ├── layout/         # AppShell, Sidebar, MobileNav
    │   │   ├── scenario/       # ChoiceButton, FeedbackToast, CompletionScreen
    │   │   └── ui/             # Avatar, ProgressBar, XPBar, Spinner, EmptyState, ErrorMessage
    │   ├── hooks/              # useAuth, useChildren, useModules, useScenario
    │   ├── pages/
    │   │   ├── auth/           # Login, Register
    │   │   ├── parent/         # Dashboard, ManageChildren, ChildDetail
    │   │   └── learn/          # ModuleBrowser, LessonList, ScenarioPlayer
    │   ├── store/              # authStore.ts (JWT in memory), scenarioStore.ts (game state)
    │   ├── styles/globals.css  # Skilio brand system
    │   ├── types/index.ts      # TypeScript interfaces mirroring backend schemas
    │   └── utils/format.ts
    ├── Dockerfile
    ├── nginx.conf              # Production static file server + SPA fallback
    ├── package.json
    └── vite.config.ts          # /api proxy → localhost:8000
```

---

## 7 · Corrections vs. Original Blueprint

The following discrepancies were found between the original Word document and the actual source code:

| Item | Original Doc | Actual Code |
|---|---|---|
| Total entities | 12 | **13** (`ModuleBadge` association table was missing) |
| Total routers | 6 | **7** (`/api/users` router was missing) |
| Total endpoints | 24 | **27** (3 `/users/me` endpoints were missing) |
| `children.avatar_url` | Not listed | **Present** — `VARCHAR(500) nullable` |
| `scenario_nodes.image_url` | Not listed | **Present** — `VARCHAR(500) nullable` |
| `scenario_choices.order_index` | Not listed | **Present** — `INTEGER default 0` |
| `badges.description` | Not listed | **Present** — `TEXT not null` |
| `badges.image_url` | Not listed | **Present** — `VARCHAR(500) nullable` |
| `lessons.description` | Not listed | **Present** — `TEXT nullable` |
| `skill_modules.thumbnail_url` | Not listed | **Present** — `VARCHAR(500) nullable` |
| `ModuleBadge` table | Not documented | **Present** — many-to-many `Badge ↔ SkillModule` |
| Axios 401 behavior | "Queues requests, refreshes token, replays all queued" | **Clears auth + redirects to `/login`** (no queuing) |
