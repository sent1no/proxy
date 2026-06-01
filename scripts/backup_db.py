"""
Резервне копіювання бази даних із шифруванням.

Запуск:
    docker compose exec api python scripts/backup_db.py

Що робить:
  1. Копіює файл БД
  2. Шифрує копію через Fernet (той самий ключ ENCRYPTION_KEY)
  3. Видаляє незашифровану копію
  4. Зберігає .db.enc у data/backups/

Правило 3-2-1:
  - 3 копії даних
  - 2 різних носії
  - 1 копія поза сайтом (offsite)
"""
import shutil
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.fernet import Fernet
from app.crypto.key_manager import get_encryption_key


def create_backup(db_path: str = "data/app.db") -> str:
    """
    Створює зашифровану резервну копію БД.

    Args:
        db_path: Шлях до файлу БД
    Returns:
        Шлях до зашифрованого файлу резервної копії
    """
    if not os.path.exists(db_path):
        print(f"❌ Файл БД не знайдено: {db_path}")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "data/backups"
    os.makedirs(backup_dir, exist_ok=True)

    # 1. Копіюємо файл БД
    backup_path = f"{backup_dir}/app_backup_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    print(f"📋 Копія створена: {backup_path}")

    # 2. Шифруємо копію
    f = Fernet(get_encryption_key())
    with open(backup_path, "rb") as file:
        data = file.read()

    encrypted_data = f.encrypt(data)
    encrypted_path = f"{backup_path}.enc"

    with open(encrypted_path, "wb") as file:
        file.write(encrypted_data)

    # 3. Видаляємо незашифровану копію
    os.remove(backup_path)

    size_kb = os.path.getsize(encrypted_path) / 1024
    print(f"🔒 Зашифрована копія: {encrypted_path} ({size_kb:.1f} KB)")
    print(f"✅ Резервна копія успішно створена!")
    return encrypted_path


def list_backups():
    """Виводить список наявних резервних копій."""
    backup_dir = "data/backups"
    if not os.path.exists(backup_dir):
        print("Резервних копій немає.")
        return

    files = sorted(os.listdir(backup_dir))
    if not files:
        print("Резервних копій немає.")
        return

    print(f"\nРезервні копії ({len(files)}):")
    for f in files:
        path = os.path.join(backup_dir, f)
        size_kb = os.path.getsize(path) / 1024
        print(f"  {f} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    create_backup()
    list_backups()
