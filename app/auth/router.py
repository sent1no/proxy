from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models import User
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user
from app.schemas import TokenResponse, TokenRefreshRequest, UserInfo, LoginRequest, UserCreate, UserResponse
from app.security import verify_password, hash_password
from app.middleware.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             summary="Реєстрація нового користувача")
@limiter.limit("10/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Реєстрація нового користувача з валідацією та санітизацією вхідних даних.
    Email шифрується автоматично через property моделі User (Практична №7).
    """
    # Перевірка унікальності username
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким логіном вже існує",
        )

    # Перевірка унікальності email — шукаємо по username, бо email зашифрований
    # Для демо: просто перевіряємо username (email унікальність на рівні БД не можна
    # перевірити через encrypted поле без розшифрування всіх записів)
    new_user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
        is_active=True,
    )
    # email.setter автоматично шифрує значення через Fernet
    new_user.email = str(user_data.email)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse, summary="Вхід та отримання JWT токенів")
@limiter.limit("5/minute")
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Аутентифікація користувача та видача Access та Refresh токенів.
    """
    username = credentials.username
    password = credentials.password

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний логін або пароль",
        )

    role = user.roles[0].name if user.roles else "student"
    access_token = create_access_token(user.id, role)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse, summary="Оновлення Access токена")
def refresh(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    """Оновлення access токена за допомогою валідного refresh токена."""
    try:
        payload = verify_token(body.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалідний refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Потрібен refresh token, а не access token",
        )

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Користувача не знайдено або заблоковано",
        )

    role = user.roles[0].name if user.roles else "student"

    return TokenResponse(
        access_token=create_access_token(user.id, role),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserInfo, summary="Інформація про поточного користувача")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Повертає дані поточного користувача.
    email розшифровується автоматично через property (Практична №7).
    """
    role = current_user.roles[0].name if current_user.roles else "student"
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,   # property → автоматично розшифровує
        full_name=current_user.full_name,
        role=role,
    )
