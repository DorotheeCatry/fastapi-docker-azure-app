from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.auth import Token, AuthData
from app.models.users import User
from app.db.session import get_session
from app.core.security import get_password_hash, verify_password, get_current_user
from app.core.jwt_handler import create_access_token

router = APIRouter()

def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit.")
    if not any(char.isupper() for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")

@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where((User.username == user.username) | (User.email == user.email))
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already in use")
    
    validate_password(user.password)
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserRead(id=db_user.id, username=db_user.username, email=db_user.email, is_active=True)

@router.post("/auth/login", response_model=Token)
async def login(form: AuthData, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == form.username)
    db_user = session.exec(statement).first()
    if not db_user or not verify_password(form.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": db_user.username, "id": db_user.id})
    return Token(access_token=access_token, token_type="bearer")

@router.post("/auth/reset-password", response_model=dict)
async def reset_password(
    request: UserUpdate, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    if request.password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password is required."
        )
    validate_password(request.password)
    
    current_user.hashed_password = get_password_hash(request.password)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return {"success": True, "message": "Password reset successfully!"}

@router.post("/auth/logout", response_model=dict)
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}
