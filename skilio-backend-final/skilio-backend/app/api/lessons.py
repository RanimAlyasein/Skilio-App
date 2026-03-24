"""
app/api/lessons.py
───────────────────
Lesson routes — individual lesson detail with entry node.

GET /api/lessons/{id}  — lesson detail including entry_node_id
                         (the client uses this to call /scenarios/nodes/{entry_node_id})
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_active_user
from app.models.lesson import Lesson
from app.schemas.module import LessonResponse

router = APIRouter()


@router.get(
    "/{lesson_id}",
    response_model=LessonResponse,
    summary="Get lesson detail",
)
def get_lesson(
    lesson_id: int,
    _=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    Returns a lesson's metadata including entry_node_id.
    The frontend uses entry_node_id to start a scenario attempt:
      POST /api/scenarios/attempts  { child_id, lesson_id }
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )

    return lesson
