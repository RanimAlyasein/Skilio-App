"""
app/schemas/scenario.py
────────────────────────
Pydantic schemas for the scenario engine.

Key design decision — ScenarioChoiceResponse does NOT include next_node_id.
The client never needs to know where a choice leads before selecting it.
That would let a player "cheat" by inspecting the response tree.
The next node is only revealed after a choice is submitted.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.scenario import AttemptStatus, NodeType
from app.schemas.base import ORMBase


# ── ScenarioNode + ScenarioChoice (read) ─────────────────────────────────────

class ScenarioChoiceResponse(ORMBase):
    """
    Returned as part of a node response.
    next_node_id is intentionally excluded — clients should not know
    where each choice leads until after they have chosen.
    """
    id: int
    choice_text: str
    is_safe_choice: bool
    feedback_text: Optional[str]
    order_index: int


class ScenarioNodeResponse(ORMBase):
    """A node plus all its available choices."""
    id: int
    lesson_id: int
    content_text: str
    image_url: Optional[str]
    node_type: NodeType
    is_correct_path: bool
    choices: list[ScenarioChoiceResponse] = []


# ── Attempt lifecycle ─────────────────────────────────────────────────────────

class AttemptCreate(BaseModel):
    """Body for POST /scenarios/attempts — starts a new play-through."""
    child_id: int = Field(..., gt=0)
    lesson_id: int = Field(..., gt=0)


class AttemptResponse(ORMBase):
    """Current state of a play-through — returned after start or resume."""
    id: int
    child_id: int
    lesson_id: int
    current_node_id: int
    status: AttemptStatus
    xp_earned: int
    started_at: datetime
    completed_at: Optional[datetime]


class AttemptWithNodeResponse(AttemptResponse):
    """
    Extended attempt response that includes the current node and its choices.
    Returned by start_attempt and advance_choice so the frontend
    only needs one round-trip to get both the attempt state and the next node.
    """
    current_node: Optional[ScenarioNodeResponse] = None


# ── Choice submission ─────────────────────────────────────────────────────────

class ChoiceSubmit(BaseModel):
    """Body for POST /scenarios/attempts/:id/choose"""
    choice_id: int = Field(..., gt=0)


class ChoiceResult(BaseModel):
    """
    Returned after a choice is submitted.

    - attempt: updated attempt state (new current_node_id, possibly completed)
    - next_node: the node the choice leads to (None if scenario is now complete)
    - feedback: the choice's feedback_text (shown briefly before advancing)
    - newly_awarded_badges: list of badge IDs just earned (for celebration UI)
    """
    attempt: AttemptResponse
    next_node: Optional[ScenarioNodeResponse]
    feedback: Optional[str]
    newly_awarded_badge_ids: list[int] = []


# ── Attempt history (for parent review) ──────────────────────────────────────

class AttemptChoiceRecord(ORMBase):
    """One step in a child's attempt history."""
    id: int
    node_id: int
    choice_id: int
    chosen_at: datetime
    # Denormalised for easy display without extra joins
    choice_text: str = ""
    node_content_preview: str = ""  # first 80 chars of node content


class AttemptHistoryResponse(ORMBase):
    """Full attempt with every choice recorded — for parent review page."""
    id: int
    child_id: int
    lesson_id: int
    status: AttemptStatus
    xp_earned: int
    started_at: datetime
    completed_at: Optional[datetime]
    choices: list[AttemptChoiceRecord] = []
