import binascii
import bcrypt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from ..models.diploma_repository import DiplomaRepository

security = HTTPBasic()

def verify_password(plain_password, hashed_password):
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    
    try:
        if hashed_password.startswith('$2a$'):
            hashed_password_bytes = hashed_password.replace('$2a$', '$2b$', 1).encode('utf-8')

        result = bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
        return result
    except (ValueError, binascii.Error):
        return False

async def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    try:   
        user = DiplomaRepository.get_user_by_username(credentials.username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль",
                headers={"WWW-Authenticate": "Basic"},
            )        
        if not verify_password(credentials.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль",
                headers={"WWW-Authenticate": "Basic"},
            )
        if not user["enabled"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь отключен",
                headers={"WWW-Authenticate": "Basic"},
            )
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка аутентификации",
            headers={"WWW-Authenticate": "Basic"},
        ) 
    