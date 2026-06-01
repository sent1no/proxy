# Electronic Dean's Office
## Опис
REST API на базі FastAPI + SQLite. Практична робота з дисципліни
"Безпека інформаційних систем".

## Виконані роботи
### Практична робота №4: Аутентифікація та безпека
- **Хешування паролів**: Bcrypt (`passlib`) для безпечного зберігання.
- **Реєстрація та Вхід**: Ендпоінти з валідацією та захистом від enumeration.

### Практична робота №5: JWT та RBAC
- **JWT (JSON Web Tokens)**: Впроваджено Access та Refresh токени для сесій.
- **RBAC (Role-Based Access Control)**: Контроль доступу на основі ролей (admin, teacher, student).
- **Middleware**: Автоматична перевірка токенів та прав доступу для захищених маршрутів.

## Запуск
```bash
git clone <url-репозиторію>
cd 8
docker compose up --build
```
## Доступ
- API: http://localhost:3010
- Документація (Swagger): http://localhost:3010/docs
- Студент: [Ваше Прізвище Ім'я]  |  Група: [Номер групи]
