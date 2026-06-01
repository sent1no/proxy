from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.audit.helpers import record_event
from app.database import SessionLocal

DOCS_PATHS = {"/docs", "/redoc", "/openapi.json"}

SENSITIVE_ACTIONS = {"POST", "PUT", "DELETE", "PATCH"}


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware Практична №8: фіксує події безпеки без читання тіла запиту."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path in DOCS_PATHS:
            return await call_next(request)

        db = SessionLocal()
        try:
            response = await call_next(request)
            status = "success"
        except Exception:
            status = "failure"
            raise
        finally:
            try:
                if request.method in SENSITIVE_ACTIONS:
                    user_id = getattr(getattr(request, "state", None), "user_id", None)
                    record_event(
                        db,
                        action={
                            "POST": "create",
                            "PUT": "update",
                            "DELETE": "delete",
                            "PATCH": "update",
                        }[request.method],
                        actor_user_id=user_id,
                        resource_type=request.url.path.split("/")[-1] or None,
                        resource_id=request.url.path,
                        status=status,
                        request=request,
                    )
                    db.commit()
            except Exception:
                db.rollback()
            finally:
                try:
                    db.close()
                except Exception:
                    pass

        return response
