from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from app.models.users import User
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from app.db.session import get_session
from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM
from fastapi import status


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


        # Fetch user from the database
        statement = select(User).where(User.username == username)
        result = db.execute(statement).first()
        user = result[0] if result else None

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")