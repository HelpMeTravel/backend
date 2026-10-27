from typing import Optional

from pydantic import BaseModel, EmailStr

# Схема для логіну
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Схема для повернення JWT токенів
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Оновлення особистих даних (Username, Email)
class UserUpdateProfile(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

# Зміна пароля
class UserChangePassword(BaseModel):
    current_password: str
    new_password: str