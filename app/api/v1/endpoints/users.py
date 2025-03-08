from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.models.users import User  # Import User model to interact with the DB
from app.schemas.user import UserRead  # Import Pydantic schema for serializing User data
from app.db.session import get_session  # Import the session dependency to interact with the DB
from app.core.jwt_handler import verify_token  # Import the function to verify JWT tokens

# Initialize the router for user-related routes
router = APIRouter()

# OAuth2 password bearer for token authentication (to be used in the header of requests)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.get("/users/me", response_model=UserRead)
def read_users_me(
    token: str = Depends(oauth2_scheme),  # Extract token from Authorization header
    session: Session = Depends(get_session)  # Get the DB session dependency
):
    """
    Endpoint to get the current authenticated user's details using the JWT token.

    Parameters:
    - `token`: The authentication token provided by the user (in the Authorization header).
    - `session`: The database session used to interact with the database.

    Returns:
    - A UserRead object containing the user's details.
    """
    # Verify the JWT token and extract the payload
    payload = verify_token(token)
    if payload is None:
        # If the token is invalid or expired, return a 401 Unauthorized error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract the username from the decoded payload (sub represents the subject)
    username: str = payload.get("sub")
    
    # Query the database for the user based on the extracted username
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()  # Execute the query and get the first result
    
    if user is None:
        # If the user is not found or the account has been deleted, return a 404 error
        raise HTTPException(status_code=404, detail="User not found or account deleted")
    
    # Return the user's data serialized according to the UserRead schema
    return user
