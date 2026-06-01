import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from .validators.sanitizer import sanitize_text


# ── Схеми для реєстрації ──

class UserCreate(BaseModel):
    """Схема для реєстрації нового користувача з суворою валідацією."""
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=30, 
        description="Логін: 3-30 символів, лише латиниця, цифри, підкреслення"
    )
    email: EmailStr = Field(..., description="Електронна пошта")
    password: str = Field(..., min_length=8, max_length=128, description="Пароль")
    full_name: str = Field(..., min_length=2, max_length=100, description="ПІБ")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Логін може містити лише латинські літери, цифри та символ підкреслення")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        # Санітизація: видалення HTML-тегів
        v = sanitize_text(v)
        if re.search(r"[<>&\"']", v):
            raise ValueError("Ім’я не може містити спеціальні символи HTML")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль повинен містити хоча б одну велику літеру")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль повинен містити хоча б одну малу літеру")
        if not re.search(r"\d", v):
            raise ValueError("Пароль повинен містити хоча б одну цифру")
        return v


class UserResponse(BaseModel):
    """Схема відповіді з даними користувача (без пароля!).
    email розшифровується автоматично через property моделі User.
    """
    id: int
    username: str
    email: str          # читається через property → розшифровується автоматично
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Схеми для входу ──

class LoginRequest(BaseModel):
    """Схема запиту на вхід."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Схема відповіді при успішному вході (v0.4 legacy)."""
    message: str
    user_id: int
    username: str
    roles: list[str] = []


# ── Схеми для JWT (v0.5) ──

class TokenResponse(BaseModel):
    """Схема відповіді з JWT токенами."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Схема запиту на оновлення токена."""
    refresh_token: str


class UserInfo(BaseModel):
    """Схема інформації про поточного користувача."""
    id: int
    username: str
    email: str
    full_name: str
    role: str

    model_config = {"from_attributes": True}
