from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from app.validators.sanitizer import sanitize_text, contains_sql_patterns

router = APIRouter(prefix="/demo", tags=["Demo / Security Testing"])


class CommentRequest(BaseModel):
    """Схема коментаря з захистом від XSS та SQL Injection."""
    text: str = Field(..., min_length=1, max_length=500, description="Текст коментаря")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v):
        # Санітизація: видалення HTML-тегів (захист від XSS)
        sanitized = sanitize_text(v)

        # Перевірка на SQL-патерни
        if contains_sql_patterns(sanitized):
            raise ValueError("Текст містить підозрілі SQL-патерни")

        # Якщо після санітизації залишились небезпечні символи — відхиляємо
        if sanitized != v:
            raise ValueError("Текст містить недозволені HTML-теги або символи")

        return sanitized


class CommentResponse(BaseModel):
    message: str
    sanitized_text: str


@router.post(
    "/comment",
    response_model=CommentResponse,
    summary="Демо: захист від XSS (тестовий ендпоінт)",
    description=(
        "Тестовий ендпоінт для перевірки захисту від XSS та SQL Injection. "
        "Спроба передати `<script>` або SQL-патерни поверне 422."
    ),
)
def post_comment(body: CommentRequest):
    """
    Приймає текст коментаря, санітизує та перевіряє на XSS/SQL Injection.
    Використовується для демонстрації захисту у Практичній №6.
    """
    return CommentResponse(
        message="Коментар прийнято. Текст безпечний.",
        sanitized_text=body.text,
    )
