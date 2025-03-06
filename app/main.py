from fastapi import FastAPI
from app.api.v1.endpoints import auth, users, loans


app = FastAPI(title="FastAPI Boilerplate")

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(loans.router, prefix="/api/v1", tags=["loans"])

