from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import bcrypt
from starlette.requests import Request
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
import os

from app.core.database import get_db
from app.models.models import User
from app.schemas.user import UserRegister, UserLogin

router = APIRouter(prefix="/auth", tags=["Auth"])

# Налаштування Google OAuth
config = Config(environ={
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET")
})
oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.post("/register")
async def register_user(user: UserRegister, db: AsyncSession = Depends(get_db)):
    # Перевірка існуючого користувача через асинхронний select
    result = await db.execute(
        select(User).filter((User.email == user.email) | (User.username == user.username))
    )
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Користувач із таким email або іменем вже існує")

    pwd_bytes = user.password.encode('utf-8')
    hashed_password = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode('utf-8')

    new_user = User(
        email=user.email,
        username=user.username,
        password_hash=hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "Користувач успішно зареєстрований", "user_id": new_user.id, "username": new_user.username}

@router.post("/login")
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).filter(User.username == user.username)
    )
    db_user = result.scalars().first()

    password_bytes = user.password.encode('utf-8')
    stored_hash_bytes = db_user.password_hash.encode('utf-8') if db_user else b""

    if not db_user or not bcrypt.checkpw(password_bytes, stored_hash_bytes):
        raise HTTPException(status_code=401, detail="Невірне ім'я користувача або пароль")

    if db_user.is_blocked:
        raise HTTPException(status_code=403, detail="Цей акаунт заблоковано")

    return {"message": "Успішний вхід", "username": db_user.username, "role": db_user.role}

@router.get("/google")
async def auth_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def auth_google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get('userinfo') or {}

    if not user_info or 'email' not in user_info:
        raise HTTPException(status_code=400, detail="Не вдалося отримати дані користувача від Google")

    email = user_info['email']
    username = user_info.get('name', email.split('@')[0])

    result = await db.execute(
        select(User).filter(User.email == email)
    )
    db_user = result.scalars().first()

    if not db_user:
        db_user = User(
            email=email,
            username=username,
            password_hash="GOOGLE_OAUTH_USER"
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

    if db_user.is_blocked:
        raise HTTPException(status_code=403, detail="Цей акаунт заблоковано")

    return {
        "message": "Успішний вхід через Google",
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role
    }