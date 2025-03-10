from fastapi import FastAPI
from app.api.v1.endpoints import auth, users, loans


app = FastAPI(
    title="Prediction Service",
    description="Online service for predicting the approval of a bank loan",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication endpoints."
        },
        {
            "name": "loans",
            "description": "Loan request and history endpoints."
        },
        {
            "name": "admin",
            "description": "Admin-related endpoints."
        }
    ]
)

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(loans.router, prefix="/api/v1", tags=["loans"])

