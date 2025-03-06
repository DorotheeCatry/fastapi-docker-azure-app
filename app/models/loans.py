from sqlmodel import SQLModel, Field, Relationship
from app.models.users import User

class LoanRequests(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    GrAppv: float = Field(default=0)
    Term : float
    State : str
    NAICS_Sectors : int
    New : str
    Franchise : str
    NoEmp : str
    RevLineCr : str
    LowDoc : str
    Rural : str
    prediction : str
    
    user: User = Relationship(back_populates="loan_requests")
