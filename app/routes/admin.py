from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth.dependencies import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", summary="Список усіх користувачів (тільки адмін)")
def list_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Лише адмін може переглядати список усіх користувачів."""
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "roles": [r.name for r in u.roles],
            "is_active": u.is_active
        }
        for u in users
    ]
