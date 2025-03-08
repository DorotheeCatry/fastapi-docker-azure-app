from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    """
    Model representing a user in the system.

    Attributes:
    - `id`: Unique identifier for the user (primary key).
    - `username`: Unique username used for authentication.
    - `email`: Unique email address of the user.
    - `hashed_password`: Hashed password of the user for security.
    - `role`: Role of the user (default is "user").
    - `is_active`: User's status, default is active.
    """
    id: Optional[int] = Field(default=None, primary_key=True)  # Primary key, optional for creation
    username: str = Field(index=True, unique=True)  # Unique username
    email: str = Field(unique=True, index=True)  # Unique email address of the user
    hashed_password: str  # Hashed password for security
    role: str = Field(nullable=False, default="user")  # User's role, default is "user"
    is_active: bool = Field(default=True)  # User's status, active by default

    # Defining the relationship with LoanRequests model (a user can have many loan requests)
    loan_requests: List["LoanRequests"] = Relationship(back_populates="user")
