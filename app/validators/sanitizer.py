import bleach
import re


def sanitize_text(text: str) -> str:
    """Видаляє ВСІ HTML-теги з тексту для запобігання XSS."""
    if not text:
        return text
    # strip=True видаляє вміст всередині тегів, якщо вони не дозволені
    cleaned = bleach.clean(text, tags=[], strip=True)
    return cleaned.strip()


def contains_sql_patterns(text: str) -> bool:
    """Перевіряє наявність підозрілих SQL-патернів."""
    if not text:
        return False
        
    sql_patterns = [
        r"(\b(UNION|SELECT|INSERT|DELETE|DROP|UPDATE)\b)",
        r"(--|;\/\*|\*\/)",
        r"(\bOR\b\s+\b1\s*=\s*1\b)",
    ]
    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
