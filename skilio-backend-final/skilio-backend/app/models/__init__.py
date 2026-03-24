"""
app/models/__init__.py
──────────────────────
Central import point for ALL SQLAlchemy models.

Alembic's autogenerate reads Base.metadata — it only knows about tables
whose model classes have been imported. Every model must be imported here.

Import order follows FK dependency: referenced tables before referencing tables.
"""

# 1. User — referenced by Child, RefreshToken
from app.models.user import User  # noqa: F401

# 2. Child — referenced by ScenarioAttempt, BadgeAward, Progress
from app.models.child import Child  # noqa: F401

# 3. SkillModule — referenced by Lesson, Progress, ModuleBadge
from app.models.module import SkillModule  # noqa: F401

# 4. Lesson — referenced by ScenarioNode (circular, use_alter), ScenarioAttempt
from app.models.lesson import Lesson  # noqa: F401

# 5. Scenario graph models
from app.models.scenario import (  # noqa: F401
    ScenarioNode,
    ScenarioChoice,
    ScenarioAttempt,
    ScenarioAttemptChoice,
    NodeType,
    AttemptStatus,
)

# 6. Progress
from app.models.progress import Progress  # noqa: F401

# 7. Badge system
from app.models.badge import Badge, BadgeAward, ModuleBadge, BadgeTriggerType  # noqa: F401

# 8. RefreshToken
from app.models.token import RefreshToken  # noqa: F401
