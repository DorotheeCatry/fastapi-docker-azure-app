from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import get_current_user
from app.db.session import get_session
from sqlmodel import Session, select
from app.models.users import User
from app.models.loans import LoanRequests
import lightgbm
import pandas as pd
import pickle
from app.core.jwt_handler import verify_token

router = APIRouter()

with open("app/utils/final_model_pipeline.pkl", "rb") as file:
    model = pickle.load(file)

request_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/loans/request")

@router.post("/loans/request")
async def request_loan_and_predict(
    loan_request: LoanRequests,
    token: str = Depends(request_scheme),
    session: Session = Depends(get_session)
):
    """
    Submits a loan request and predicts approval status
    """
    current_user = get_current_user(token, session)
    current_user_id = current_user.id

    # Convert Yes/No to 1/0 for binary fields
    franchise = 1 if loan_request.Franchise == "Yes" else 0
    new = 1 if loan_request.New == "Yes" else 0
    rev_line_cr = 1 if loan_request.RevLineCr == "Yes" else 0
    low_doc = 1 if loan_request.LowDoc == "Yes" else 0
    rural = 1 if loan_request.Rural == "Yes" else 0

    loan_data = {
        "GrAppv": [float(loan_request.GrAppv)],
        "Term": [float(loan_request.Term)],
        "State": [loan_request.State],
        "NAICS_Sectors": [loan_request.NAICS_Sectors],
        "New": [new],
        "Franchise": [franchise],
        "NoEmp": [float(loan_request.NoEmp)],
        "RevLineCr": [rev_line_cr],
        "LowDoc": [low_doc],
        "Rural": [rural]
    }

    df_data = pd.DataFrame(loan_data)

    try:
        prediction = model.predict(df_data)
        pred = bool(prediction[0])

        loan_request_data = LoanRequests(
            user_id=current_user_id,
            GrAppv=loan_request.GrAppv,
            Term=loan_request.Term,
            State=loan_request.State,
            NAICS_Sectors=loan_request.NAICS_Sectors,
            New=loan_request.New,
            Franchise=loan_request.Franchise,
            NoEmp=loan_request.NoEmp,
            RevLineCr=loan_request.RevLineCr,
            LowDoc=loan_request.LowDoc,
            Rural=loan_request.Rural,
            prediction=pred
        )
        
        session.add(loan_request_data)
        session.commit()
        
        return pred
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/loans/history")
async def get_loan_history(
    token: str = Depends(request_scheme),
    session: Session = Depends(get_session)
):
    """
    Retrieves loan request history
    """
    try:
        current_user = get_current_user(token, session)
        
        if current_user.role == "admin":
            loans = session.exec(select(LoanRequests)).all()
        else:
            loans = session.exec(
                select(LoanRequests).where(LoanRequests.user_id == current_user.id)
            ).all()

        if not loans:
            return []
        
        return loans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))