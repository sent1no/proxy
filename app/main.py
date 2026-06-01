from fastapi import FastAPI
from app import models
from app.auth.router import router as auth_router
from app.routes.students import router as students_router
from app.routes.teachers import router as teachers_router
from app.routes.admin import router as admin_router

from fastapi.middleware.cors import CORSMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limiter import limiter

app = FastAPI(
    title="Електронний деканат",
    description="API для управління академічними даними з JWT та RBAC (Secure Edition)",
    version="0.6.0"
)

# 1. Додавання HTTP Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 2. Налаштування CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", # Наприклад, для React/Next.js
        "http://localhost:3010",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# 3. Підключення Rate Limiter до FastAPI state
app.state.limiter = limiter

# Підключення роутерів
app.include_router(auth_router)
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {"message": "Електронний деканат API v0.4.0"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "SQLite",
        "tables": len(models.Base.metadata.tables)
    }
