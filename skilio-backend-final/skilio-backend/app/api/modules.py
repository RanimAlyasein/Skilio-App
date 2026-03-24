"""
app/api/modules.py
───────────────────
SkillModule read routes — browsable by any authenticated user.

GET  /api/modules/           — list all published modules (with optional age filter)
GET  /api/modules/{id}       — module detail with lesson list

Modules are content managed by admins (out of MVP scope), so only
GET routes are exposed here. POST/PUT are stubs that can be enabled later.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_db, require_active_user
from app.models.module import SkillModule
from app.schemas.module import SkillModuleResponse, SkillModuleWithLessons

router = APIRouter()


@router.get(
    "/",
    response_model=list[SkillModuleResponse],
    summary="List all published skill modules",
)
def list_modules(
    age: Optional[int] = Query(
        None,
        ge=4,
        le=17,
        description="Filter modules appropriate for this age",
    ),
    _=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    Returns all published skill modules.
    Optional ?age= query parameter filters to modules whose age range
    includes the given age — useful for showing age-appropriate content.
    """
    query = db.query(SkillModule).filter(SkillModule.is_published == True)  # noqa: E712

    if age is not None:
        query = query.filter(
            SkillModule.age_min <= age,
            SkillModule.age_max >= age,
        )

    return query.order_by(SkillModule.order_index).all()


@router.get(
    "/{module_id}",
    response_model=SkillModuleWithLessons,
    summary="Get a module with its full lesson list",
)
def get_module(
    module_id: int,
    _=Depends(require_active_user),
    db: Session = Depends(get_db),
):
    """
    Returns a module and its ordered list of lessons.
    Used on the lesson list page.
    """
    module = (
        db.query(SkillModule)
        .options(joinedload(SkillModule.lessons))
        .filter(
            SkillModule.id == module_id,
            SkillModule.is_published == True,  # noqa: E712
        )
        .first()
    )

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )

    return module
