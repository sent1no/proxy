from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.auth.dependencies import require_role
from app.database import get_db
from app.models import AuditLog, User

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs", summary="Перегляд журналу подій")
def list_audit_logs(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Адмін отримує останні записи audit_log."""
    rows = (
        db.query(AuditLog)
        .order_by(desc(AuditLog.timestamp))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "total": db.query(AuditLog).count(),
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": row.id,
                "timestamp": row.timestamp.isoformat(),
                "actor_id": row.actor_user_id,
                "action": row.action,
                "resource_type": row.resource_type,
                "resource_id": row.resource_id,
                "ip": row.ip_address,
                "user_agent": row.user_agent,
                "status": row.status,
                "details": row.details,
            }
            for row in rows
        ],
    }
