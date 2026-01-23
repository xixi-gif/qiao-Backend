from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from app.api.crud.user import authenticate_user, get_user_by_id, get_user_by_phone
from app.api.utils.security import create_access_token
from app.api.core.config import settings
from app.api.schemas.user import Token
from app.api.db.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def create_token_response(user) -> Token:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_info={
            "id": user.id,
            "username": user.username,
            "phone": user.phone,
            "role": user.role.value,
            "avatar": user.avatar
        }
    )


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录态已失效，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_id(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
    return user