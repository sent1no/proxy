import os

# КРИТИЧНО: у продакшні SECRET_KEY береться зі змінної оточення
# openssl rand -hex 32
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-dev-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
