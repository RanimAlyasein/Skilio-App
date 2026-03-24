// ─────────────────────────────────────────────────────────────────────────────
// src/types/index.ts
// TypeScript interfaces that mirror the FastAPI/Pydantic response schemas.
// Keep these in sync with app/schemas/* in the backend.
// ─────────────────────────────────────────────────────────────────────────────

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  created_at: string
}

export interface Token {
  access_token: string
  token_type: 'bearer'
}

export interface LoginCredentials {
  username: string   // FastAPI OAuth2PasswordRequestForm uses 'username'
  password: string
}

export interface RegisterPayload {
  email: string
  full_name: string
  password: string
}

// ── Child ─────────────────────────────────────────────────────────────────────

export interface Child {
  id: number
  parent_id: number
  display_name: string
  age: number
  avatar_url: string | null
  total_xp: number
  is_active: boolean
  created_at: string
}

export interface ChildSummary {
  id: number
  display_name: string
  age: number
  avatar_url: string | null
  total_xp: number
}

export interface ChildCreate {
  display_name: string
  age: number
  avatar_url?: string | null
}

export interface ChildUpdate {
  display_name?: string
  age?: number
  avatar_url?: string | null
}

// ── Skill Module & Lesson ─────────────────────────────────────────────────────

export interface SkillModule {
  id: number
  title: string
  description: string
  thumbnail_url: string | null
  age_min: number
  age_max: number
  is_published: boolean
  order_index: number
  created_at: string
}

export interface SkillModuleWithLessons extends SkillModule {
  lessons: Lesson[]
}

export interface Lesson {
  id: number
  module_id: number
  title: string
  description: string | null
  xp_reward: number
  order_index: number
  entry_node_id: number | null
  created_at: string
}

// ── Scenario ──────────────────────────────────────────────────────────────────

export type NodeType = 'start' | 'branch' | 'end'
export type AttemptStatus = 'in_progress' | 'completed' | 'abandoned'

export interface ScenarioChoice {
  id: number
  choice_text: string
  is_safe_choice: boolean
  feedback_text: string | null
  order_index: number
  // NOTE: next_node_id is intentionally NOT in this type — the backend
  // excludes it from responses to prevent clients from peeking ahead.
}

export interface ScenarioNode {
  id: number
  lesson_id: number
  content_text: string
  image_url: string | null
  node_type: NodeType
  is_correct_path: boolean
  choices: ScenarioChoice[]
}

export interface ScenarioAttempt {
  id: number
  child_id: number
  lesson_id: number
  current_node_id: number
  status: AttemptStatus
  xp_earned: number
  started_at: string
  completed_at: string | null
}

export interface AttemptWithNode extends ScenarioAttempt {
  current_node: ScenarioNode | null
}

export interface ChoiceResult {
  attempt: ScenarioAttempt
  next_node: ScenarioNode | null
  feedback: string | null
  newly_awarded_badge_ids: number[]
}

export interface AttemptChoiceRecord {
  id: number
  node_id: number
  choice_id: number
  chosen_at: string
  choice_text: string
  node_content_preview: string
}

export interface AttemptHistory extends ScenarioAttempt {
  choices: AttemptChoiceRecord[]
}

// ── Progress ──────────────────────────────────────────────────────────────────

export interface Progress {
  id: number
  child_id: number
  module_id: number
  lessons_completed: number
  total_lessons: number
  last_activity_at: string
  completion_percentage: number
}

export interface ModuleProgress {
  module_id: number
  module_title: string
  lessons_completed: number
  total_lessons: number
  completion_percentage: number
  last_activity_at: string | null
}

// ── Badge ─────────────────────────────────────────────────────────────────────

export type BadgeTriggerType =
  | 'first_lesson'
  | 'lesson_count'
  | 'module_complete'
  | 'xp_milestone'
  | 'safe_choices'

export interface Badge {
  id: number
  name: string
  description: string
  image_url: string | null
  trigger_type: BadgeTriggerType
  trigger_value: number
  xp_bonus: number
  is_active: boolean
}

export interface BadgeAward {
  id: number
  child_id: number
  badge_id: number
  awarded_at: string
  badge: Badge
}

// ── Dashboard summary ─────────────────────────────────────────────────────────

export interface ChildDashboard {
  child_id: number
  display_name: string
  age: number
  avatar_url: string | null
  total_xp: number
  module_progress: ModuleProgress[]
  badges_earned: BadgeAward[]
  recent_attempt_count: number
}

// ── API error ─────────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string | { msg: string; type: string }[]
}
