from fastapi import APIRouter, HTTPException, Depends
from app.core.security import get_current_user
from app.db.session import get_session
from sqlmodel import Session, select
from app.models.users import User
from app.models.loans import LoanRequests
import lightgbm
import pandas as pd
import pickle

router = APIRouter()

with open("app/utils/final_model_pipeline.pkl", "rb") as file:
    model = pickle.load(file)


@router.post("/loans/request")
async def request_loan_and_predict(loan_request: LoanRequests, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):

    # Prepare loan data
    loan_data = {
        "GrAppv": [loan_request.GrAppv],
        "Term": [loan_request.Term],
        "State": [loan_request.State],
        "NAICS_Sectors": [loan_request.NAICS_Sectors],
        "New": [loan_request.New],
        "Franchise": [loan_request.Franchise],
        "NoEmp" : [loan_request.NoEmp],
        "RevLineCr": [loan_request.RevLineCr],
        "LowDoc": [loan_request.LowDoc],
        "Rural": [loan_request.Rural]        
    }
        
    df_data = pd.DataFrame(loan_data)
    df_data["GrAppv"] = df_data["GrAppv"].astype("float32")
    df_data["Term"] = df_data["Term"].astype("float32")
    df_data["State"] = df_data["State"].astype("str")
    df_data["NAICS_Sectors"] = df_data["NAICS_Sectors"].astype("str")
    df_data["New"] = df_data["New"].astype("str")
    df_data["Franchise"] = df_data["Franchise"].astype("float")
    df_data["NoEmp"] = df_data["NoEmp"].astype("float32")
    df_data["RevLineCr"] = df_data["RevLineCr"].astype("str")
    df_data["LowDoc"] = df_data["LowDoc"].astype("str")
    df_data["Rural"] = df_data["Rural"].astype("str")

    # Predict loan status
    prediction = model.predict(df_data)
    pred = True if prediction[0] == 1 else False
    
    
    api_user_id = current_user

    # Save the loan request data to the database
    loan_request_data = LoanRequests(
        user_id=api_user_id,
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
        prediction=pred  # add the predicted result
    )
    
    print(loan_data)
    print(df_data)
    print(loan_request_data)
    session.add(loan_request_data)
    session.commit()

    return pred

    

@router.get("/loans/history")
async def get_loan_history(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    # Utilisation de l'ID de l'utilisateur actuel
    user_id = current_user["id"]
    
    # Récupérer les prêts associés à l'ID de l'utilisateur
    loans = session.exec(select(LoanRequests).where(LoanRequests.user_id == user_id)).all()
    
    # Si aucun prêt n'est trouvé, renvoyer une erreur 404
    if not loans:
        raise HTTPException(status_code=404, detail="No loan requests found")
    
    # Retourner l'historique des prêts
    return loans