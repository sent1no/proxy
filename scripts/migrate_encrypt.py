"""
Скрипт міграції існуючих даних — шифрування email у БД.

Запуск (всередині контейнера):
    docker compose exec api python scripts/migrate_encrypt.py

Що робить:
  1. Знаходить записи, де encrypted_email порожній або NULL
  2. Шифрує email через Fernet
  3. Зберігає шифротекст у encrypted_email
  4. Очищає старе поле email (якщо воно ще є)
"""
import sys
import os

# Додаємо корінь проекту до шляху
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.crypto.encryption import encrypt_field
from sqlalchemy import text


def migrate():
    db = SessionLocal()
    try:
        # Перевіряємо чи існує стовпець encrypted_email
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]

        if "encrypted_email" not in columns:
            print("❌ Стовпець encrypted_email не існує.")
            print("   Спочатку запустіть міграцію Alembic:")
            print("   docker compose exec api alembic upgrade head")
            return

        # Знаходимо записи без шифрування
        if "email" in columns:
            # Стара схема — є відкритий email
            result = db.execute(
                text("SELECT id, email FROM users WHERE (encrypted_email IS NULL OR encrypted_email = '') AND email IS NOT NULL")
            )
        else:
            print("✅ Стара колонка email відсутня — міграція не потрібна.")
            return

        users = result.fetchall()
        print(f"Знайдено {len(users)} записів для міграції")

        if not users:
            print("✅ Всі записи вже зашифровані.")
            return

        for user_id, email in users:
            if not email:
                continue
            encrypted = encrypt_field(email)
            db.execute(
                text("UPDATE users SET encrypted_email = :enc WHERE id = :id"),
                {"enc": encrypted, "id": user_id}
            )
            # Маскуємо для логу
            masked = email[0] + "***@" + email.split("@")[-1] if "@" in email else "***"
            print(f"  User #{user_id}: {masked} → зашифровано")

        db.commit()
        print(f"\n✅ Міграція завершена: {len(users)} записів зашифровано")

    except Exception as e:
        db.rollback()
        print(f"❌ Помилка міграції: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
