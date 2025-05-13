from sqlmodel import SQLModel, Field, Relationship
from app.models.users import User


class LoanRequests(SQLModel, table=True):
    """
    Represents a loan request, including details about the loan and its status.
    """
    id: int = Field(default=None, primary_key=True)             # Loan request ID
    user_id: int = Field(foreign_key="user.id")                 # Foreign key to User table
    GrAppv: float = Field(default=0)                            # Loan amount
    Term: float                                                 # Loan term (months or years)
    State: str                                                  # State of the loan request
    NAICS_Sectors: int                                          # NAICS code for the business sector
    New: str                                                    # Indicates if the business is new ('Yes' or 'No')
    Franchise: str                                              # Indicates if the business is a franchise ('Yes' or 'No')
    NoEmp: str                                                  # Number of employees
    RevLineCr: str                                              # Revolving line of credit ('Yes' or 'No')
    LowDoc: str                                                 # Low documentation request ('Yes' or 'No')
    Rural: str                                                  # Rural area loan request ('Yes' or 'No')
    prediction: str                                             # Predicted loan outcome (approved/rejected)

    user: User = Relationship(back_populates="loan_requests")   # Relationship to User model
