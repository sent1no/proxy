from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

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
            "email": u.email,          # property → автоматично розшифровує
            "roles": [r.name for r in u.roles],
            "is_active": u.is_active
        }
        for u in users
    ]


@router.get("/encryption-check",
            summary="Перевірка шифрування у БД (тільки адмін)")
def check_encryption(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Практична №7: показує що у БД зберігається шифротекст,
    а через API повертається розшифрований email.
    """
    result = db.execute(
        text("SELECT username, encrypted_email FROM users LIMIT 5")
    )
    rows = result.fetchall()

    data = []
    for username, encrypted_email in rows:
        data.append({
            "username": username,
            "in_db_encrypted": encrypted_email[:60] + "..." if encrypted_email else None,
            "via_api_decrypted": db.query(User).filter(
                User.username == username
            ).first().email,
        })

    return {
        "message": "Email у БД зашифровано, через API — розшифровано автоматично",
        "users": data
    }
