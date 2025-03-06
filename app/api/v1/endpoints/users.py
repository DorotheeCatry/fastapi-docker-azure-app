from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.models.users import User
from app.schemas.user import UserRead
from app.db.session import get_session
from app.core.jwt_handler import verify_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

@router.get("/users/me", response_model=UserRead)
def read_users_me(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'authentification invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=404, detail="L'utilisateur a été supprimé, token invalide")
    return user