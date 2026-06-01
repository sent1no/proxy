"""
Управління ключами шифрування.
Ключ береться виключно зі змінної оточення ENCRYPTION_KEY.
Ніколи не зберігайте ключ у коді або Git!
"""
import os
import sys


def get_encryption_key() -> bytes:
    """
    Отримує ключ Fernet зі змінної оточення ENCRYPTION_KEY.
    Якщо ключ не встановлено — завершує роботу з помилкою.
    """
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        print("КРИТИЧНА ПОМИЛКА: ENCRYPTION_KEY не встановлено!")
        print("   Запустіть: python scripts/generate_key.py")
        print("   Потім додайте ключ до docker-compose.yml → environment")
        sys.exit(1)
    return key.encode()
