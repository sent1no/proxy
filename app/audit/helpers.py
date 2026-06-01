from __future__ import annotations

import re
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.database import Base
from app.models import AuditLog

# Храним текущий request для того, чтобы middleware мог проставить контекст
current_request: ContextVar[Optional[Request]] = ContextVar(
    "current_request", default=None
)

# Паттерны подозрительной активности
SUSPICIOUS_SCRIPTS = re.compile(r"<script|javascript:|onerror\s*=|onload\s*=", re.IGNORECASE)
SUSPICIOUS_SQL = re.compile(
    r"\b(union\s+all\s+select|select\s+.*\s+from|drop\s+table|delete\s+from|"
    r"insert\s+into|update\s+.*\s+set|exec\s+|xp_|--|/\*|\*/)\b",
    re.IGNORECASE | re.VERBOSE,
)


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


def _get_user_agent(request: Request) -> str:
    return request.headers.get("user-agent", "")[:255]


def detect_suspicious(text: Optional[str]) -> bool:
    if not text:
        return False
    return bool(SUSPICIOUS_SCRIPTS.search(text) or SUSPICIOUS_SQL.search(text))


def record_event(
    db: Session,
    *,
    action: str,
    actor_user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    status: str = "success",
    details: Optional[str] = None,
    request: Optional[Request] = None,
) -> None:
    """Писать событие в audit_log без коммита. Коммит делает вызывающий код."""
    request = request or current_request.get()
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=_get_client_ip(request) if request else None,
        user_agent=_get_user_agent(request) if request else None,
        status=status,
        details=details,
    )
    db.add(entry)
