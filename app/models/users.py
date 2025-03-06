from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role : str = Field(nullable=False, default="user")
    is_active: bool = Field(default=True)
    
    loan_requests: list["LoanRequests"] = Relationship(back_populates="user")

