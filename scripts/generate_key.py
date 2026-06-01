"""
Генерація ключа Fernet для шифрування персональних даних.

Запуск:
    python scripts/generate_key.py

Потім скопіюйте ENCRYPTION_KEY= у docker-compose.yml → environment.
НІКОЛИ не зберігайте ключ у Git!
"""
from cryptography.fernet import Fernet

key = Fernet.generate_key()

print("=" * 60)
print("  Згенерований ключ Fernet (AES-128-CBC)")
print("=" * 60)
print()
print(f"ENCRYPTION_KEY={key.decode()}")
print()
print("⚠️  УВАГА:")
print("  - Цей ключ — єдиний спосіб розшифрувати дані.")
print("  - Втрата ключа = втрата всіх зашифрованих даних.")
print("  - Ніколи не зберігайте ключ у Git або коді.")
print("  - У production використовуйте HashiCorp Vault або AWS KMS.")
print()
print("Додайте до docker-compose.yml → environment:")
print(f"  - ENCRYPTION_KEY={key.decode()}")
print("=" * 60)
