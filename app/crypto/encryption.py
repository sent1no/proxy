"""
Модуль шифрування/розшифрування полів БД через Fernet (AES-128-CBC + HMAC-SHA256).

Властивості Fernet:
- Симетричне шифрування (один ключ для encrypt/decrypt)
- Кожен виклик encrypt генерує унікальний результат (випадковий IV)
- Вбудована перевірка цілісності через HMAC — підроблені дані не розшифруються
- Вбудований timestamp
"""
from cryptography.fernet import Fernet, InvalidToken
from app.crypto.key_manager import get_encryption_key


def get_fernet() -> Fernet:
    """Створює об'єкт Fernet з поточним ключем зі змінної оточення."""
    return Fernet(get_encryption_key())


def encrypt_field(value: str) -> str:
    """
    Шифрує рядкове значення за допомогою Fernet.
    Кожен виклик генерує різний шифротекст (випадковий IV) — це нормально.

    Args:
        value: Відкритий текст (наприклад, email або телефон)
    Returns:
        Зашифрований рядок у форматі base64 (gAAAAAB...)
    """
    if not value:
        return value
    f = get_fernet()
    encrypted = f.encrypt(value.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_field(encrypted_value: str) -> str:
    """
    Розшифровує значення, зашифроване encrypt_field.
    При невірному ключі або підробленому шифротексті повертає повідомлення про помилку.

    Args:
        encrypted_value: Зашифрований рядок (gAAAAAB...)
    Returns:
        Розшифрований оригінальний рядок або повідомлення про помилку
    """
    if not encrypted_value:
        return encrypted_value
    try:
        f = get_fernet()
        decrypted = f.decrypt(encrypted_value.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken:
        return "[ПОМИЛКА РОЗШИФРУВАННЯ — невірний ключ або пошкоджені дані]"
    except Exception:
        return "[ПОМИЛКА РОЗШИФРУВАННЯ]"
