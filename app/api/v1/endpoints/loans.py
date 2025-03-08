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
    loan_request: LoanRequests,  # The loan request data to be processed.
    token: str = Depends(request_scheme),  # Token used to authenticate the user making the request.
    session: Session = Depends(get_session)  # Dependency to access the database session.
):
    """
    Submits a loan request, predicts the loan approval status, 
    and records the loan request data in the database.

    Parameters:
    - `loan_request` (LoanRequests): Data related to the loan request, such as loan amount, term, business sector, etc.
    - `token` (str): Token used to authenticate the user making the request.
    - `session` (Session): The database session for interacting with the database.

    This function processes a loan request by first authenticating the user with the provided token. 
    It then uses the loan request data to predict the loan approval status using a pre-trained model 
    and records the loan request and prediction results in the database.
    """
    
    # Retrieve the current user based on the provided token.
    current_user = get_current_user(token, session)
    current_user_id = current_user.id  # Use the current user's ID for database operations.

    # Prepare the loan data to be passed into the prediction model.
    loan_data = {
        "GrAppv": [loan_request.GrAppv],
        "Term": [loan_request.Term],
        "State": [loan_request.State],
        "NAICS_Sectors": [loan_request.NAICS_Sectors],
        "New": [loan_request.New],
        "Franchise": [loan_request.Franchise],
        "NoEmp": [loan_request.NoEmp],
        "RevLineCr": [loan_request.RevLineCr],
        "LowDoc": [loan_request.LowDoc],
        "Rural": [loan_request.Rural]        
    }

    # Convert the loan data into a DataFrame to be processed by the prediction model.
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

    # Use the pre-trained model to predict whether the loan request is approved or not.
    prediction = model.predict(df_data)
    pred = True if prediction[0] == 1 else False  # Convert the model's output to a boolean.

    # Create a new loan request entry in the database with the provided data and prediction result.
    loan_request_data = LoanRequests(
        user_id=current_user_id,  # Link the loan request to the authenticated user.
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
        prediction=pred  # Store the prediction result in the database.
    )
    
    # Save the loan request data to the database.
    session.add(loan_request_data)
    session.commit()  # Commit the transaction to persist the data.

    # Return the prediction result (True for approved, False for not approved).
    return pred


@router.get("/loans/history")
async def get_loan_history(token: str = Depends(request_scheme), session: Session = Depends(get_session)):
    """
    Retrieves the loan history for the authenticated user or admin.

    Parameters:
    - `token` (str): Token used to authenticate the user making the request.
    
    This function verifies the provided token, retrieves the user associated with it,
    and returns a list of loan requests. If the user is an admin, all loan requests are returned.
    If the user is a regular user, only their own loan requests are returned.
    If no loan requests are found, a 404 error is raised.
    """
    # Retrieve the user from the token
    current_user = get_current_user(token, session)
    
    # Extract user_id from the authenticated user
    user_id = current_user.id
    
    try:
        # Check if the user is an admin or a regular user
        if current_user.role == "admin":
            # Admins can see all loan requests
            loans = session.exec(select(LoanRequests)).all()
        else:
            # Regular users can only see their own loan requests
            loans = session.exec(select(LoanRequests).where(LoanRequests.user_id == user_id)).all()

        # If no loan requests are found, raise a 404 error
        if not loans:
            raise HTTPException(status_code=404, detail="No loan requests found")
        
        # Return the list of loan requests
        return loans
    
    except Exception as ex:
        # Handle any errors that might occur during the process
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(ex)}")
