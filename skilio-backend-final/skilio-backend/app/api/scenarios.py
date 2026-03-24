"""
app/api/scenarios.py
─────────────────────
Scenario engine HTTP routes.

POST /api/scenarios/attempts                    — start or resume a play-through
GET  /api/scenarios/attempts/{id}               — get current attempt state + node
POST /api/scenarios/attempts/{id}/choose        — submit a choice, advance to next node
GET  /api/scenarios/attempts/{id}/history       — full choice audit trail (parent review)
GET  /api/scenarios/nodes/{id}                  — get a single node with its choices

The router keeps HTTP concerns here (status codes, HTTPException conversion).
All game logic lives in app/services/scenario_service.py.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_owned_attempt, require_active_user
from app.crud import crud_scenario as db_scenario
from app.schemas.scenario import (
    AttemptCreate,
    AttemptHistoryResponse,
    AttemptWithNodeResponse,
    ChoiceResult,
    ChoiceSubmit,
    ScenarioNodeResponse,
    AttemptChoiceRecord,
)

router = APIRouter()


@router.post(
    "/attempts",
    response_model=AttemptWithNodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start or resume a scenario attempt",
)
def start_attempt(
    body: AttemptCreate,
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    Creates a new ScenarioAttempt at the lesson's entry node.
    If an in-progress attempt already exists for this child+lesson, it is
    returned instead — allowing seamless resume after app restart.

    Returns the attempt state AND the current node with choices, so the
    frontend needs only one request to render the first screen.
    """
    from app.services.scenario_service import start_attempt as svc_start

    try:
        attempt = svc_start(
            db,
            child_id=body.child_id,
            lesson_id=body.lesson_id,
            parent_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    current_node = db_scenario.get_node_with_choices(db, attempt.current_node_id)

    return AttemptWithNodeResponse(
        id=attempt.id,
        child_id=attempt.child_id,
        lesson_id=attempt.lesson_id,
        current_node_id=attempt.current_node_id,
        status=attempt.status,
        xp_earned=attempt.xp_earned,
        started_at=attempt.created_at,
        completed_at=attempt.completed_at,
        current_node=current_node,
    )


@router.get(
    "/attempts/{attempt_id}",
    response_model=AttemptWithNodeResponse,
    summary="Get current attempt state (for resume)",
)
def get_attempt(
    attempt=Depends(get_owned_attempt),
    db: Session = Depends(get_db),
):
    """
    Returns the current state of an attempt including the current node.
    Used to resume a mid-session play-through after browser refresh.
    """
    current_node = db_scenario.get_node_with_choices(db, attempt.current_node_id)

    return AttemptWithNodeResponse(
        id=attempt.id,
        child_id=attempt.child_id,
        lesson_id=attempt.lesson_id,
        current_node_id=attempt.current_node_id,
        status=attempt.status,
        xp_earned=attempt.xp_earned,
        started_at=attempt.created_at,
        completed_at=attempt.completed_at,
        current_node=current_node,
    )


@router.post(
    "/attempts/{attempt_id}/choose",
    response_model=ChoiceResult,
    summary="Submit a choice and advance the scenario",
)
def submit_choice(
    body: ChoiceSubmit,
    attempt=Depends(get_owned_attempt),
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    The core engine endpoint.

    Accepts a choice_id, validates it against the current node, records it,
    and advances the attempt to the next node.

    Response includes:
    - Updated attempt state
    - Next node with choices (or null if scenario is complete)
    - Feedback text from the choice
    - Any badge IDs just earned (for the celebration screen)
    """
    from app.services.scenario_service import advance_choice

    try:
        result = advance_choice(
            db,
            attempt_id=attempt.id,
            choice_id=body.choice_id,
            parent_id=current_user.id,
        )
    except ValueError as e:
        error_msg = str(e)
        if "already" in error_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    return result


@router.get(
    "/attempts/{attempt_id}/history",
    response_model=AttemptHistoryResponse,
    summary="Get full choice audit trail for an attempt (parent review)",
)
def get_attempt_history(
    attempt=Depends(get_owned_attempt),
    db: Session = Depends(get_db),
):
    """
    Returns the complete ordered list of choices made during an attempt.
    Used on the parent's child detail page to show exactly what path
    their child took through a scenario.
    """
    raw_choices = db_scenario.get_attempt_choices(db, attempt.id)

    choice_records = [
        AttemptChoiceRecord(
            id=ac.id,
            node_id=ac.node_id,
            choice_id=ac.choice_id,
            chosen_at=ac.chosen_at,
            choice_text=ac.choice.choice_text if ac.choice else "",
            node_content_preview=(ac.node.content_text[:80] + "…")
            if ac.node and len(ac.node.content_text) > 80
            else (ac.node.content_text if ac.node else ""),
        )
        for ac in raw_choices
    ]

    return AttemptHistoryResponse(
        id=attempt.id,
        child_id=attempt.child_id,
        lesson_id=attempt.lesson_id,
        status=attempt.status,
        xp_earned=attempt.xp_earned,
        started_at=attempt.created_at,
        completed_at=attempt.completed_at,
        choices=choice_records,
    )


@router.get(
    "/nodes/{node_id}",
    response_model=ScenarioNodeResponse,
    summary="Get a scenario node with its available choices",
)
def get_node(
    node_id: int,
    _=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    Returns a single scenario node and its choices.
    Note: choices do NOT include next_node_id — the destination is only
    revealed after the choice is submitted via /attempts/{id}/choose.
    """
    node = db_scenario.get_node_with_choices(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )
    return node
