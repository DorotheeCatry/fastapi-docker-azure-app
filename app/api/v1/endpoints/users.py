from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.models.users import User
from app.schemas.user import UserRead, UserCreate
from app.db.session import get_session
from app.core.jwt_handler import verify_token
from app.core.security import get_password_hash, get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.get("/users/me", response_model=UserRead)
def read_users_me(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    """Get current user profile"""
    current_user = get_current_user(token, session)
    return current_user

@router.post("/admin/users", response_model=UserRead)
def create_user(
    user: UserCreate,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    """Create a new user (admin only)"""
    current_user = get_current_user(token, session)
    
    if not current_user or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users"
        )

    existing_user = session.exec(
        select(User).where(User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists"
        )

    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        is_active=False
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

@router.get("/admin/users")
def get_users(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all users (admin only)"""
    if not current_user or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )

    users = session.exec(select(User)).all()
    return {"Users": [user.username for user in users]}