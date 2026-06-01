from fastapi import FastAPI
from app import models
from app.config import APP_PORT
from app.auth.router import router as auth_router
from app.routes.students import router as students_router
from app.routes.teachers import router as teachers_router
from app.routes.admin import router as admin_router
from app.routes.demo import router as demo_router
from app.routes.audit import router as audit_router

from fastapi.middleware.cors import CORSMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limiter import limiter
from app.middleware.audit_middleware import AuditMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

app = FastAPI(
    title="Електронний деканат",
    description="API для управління академічними даними з JWT та RBAC (Secure Edition)",
    version="0.8.0",
)

# 0. Rate Limit — обробник помилок + state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 1. HTTP Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 2. Audit middleware (Практична №8)
app.add_middleware(AuditMiddleware)

# 3. CORS — дозволені origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:3010",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# Підключення роутерів
app.include_router(auth_router)
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)
app.include_router(demo_router)
app.include_router(audit_router)


@app.get("/")
def root():
    return {"message": "Електронний деканат API v0.8.0"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "SQLite",
        "tables": len(models.Base.metadata.tables),
    }
