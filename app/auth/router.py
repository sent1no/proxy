from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models import User
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user
from app.schemas import TokenResponse, TokenRefreshRequest, UserInfo
from app.security import verify_password
from app.middleware.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="Вхід та отримання JWT токенів")
@limiter.limit("5/minute")
def login(request: Request, credentials: dict, db: Session = Depends(get_db)):
    """
    Аутентифікація користувача та видача Access та Refresh токенів.
    """
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необхідно вказати username та password"
        )

    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний логін або пароль",
        )

    # Визначаємо основну роль (беремо першу)
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
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Користувача не знайдено"
        )

    role = user.roles[0].name if user.roles else "student"
    
    return TokenResponse(
        access_token=create_access_token(user.id, role),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserInfo, summary="Інформація про поточного користувача")
def get_me(current_user: User = Depends(get_current_user)):
    """Повертає дані користувача, витягнуті з JWT токена."""
    role = current_user.roles[0].name if current_user.roles else "student"
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=role,
    )
