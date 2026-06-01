# Electronic Dean's Office
REST API на базі FastAPI + SQLite. Практичні роботи з дисципліни "Безпека інформаційних систем".

## Виконані роботи
- Практична №4: Аутентифікація (Bcrypt, хешування паролів)
- Практична №5: JWT та RBAC (Access/Refresh токени)
- Практична №6: Веб-безпека (CSP, Security Headers, XSS, Rate Limit)
- Практична №7: Field-Level Encryption (Fernet/AES для email, телефон, backup)
- Практична №8: Аудит безпеки (audit_log, AuditMiddleware, /audit/logs)

## Запуск
```bash
cp .env.example .env    # відредагуйте .env під себе
docker compose up --build
```
Або без Docker:
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Доступ
- API: http://localhost:8000
- Документація (Swagger): http://localhost:8000/docs
- Health: http://localhost:8000/health

## Додаткові скрипти
```bash
python scripts/generate_key.py
python scripts/backup_db.py
python scripts/migrate_encrypt.py
alembic upgrade head
```