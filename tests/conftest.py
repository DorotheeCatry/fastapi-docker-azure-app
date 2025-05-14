import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.session import get_session
from app.models.users import User
from app.models.loans import LoanRequests
from app.core.security import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user_fixture(session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("userpass"),
        role="user",
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(name="test_admin")
def test_admin_fixture(session):
    admin = User(
        username="testadmin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass"),
        role="admin",
        is_active=True
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin

@pytest.fixture(name="test_loan")
def test_loan_fixture(session, test_user):
    loan = LoanRequests(
        user_id=test_user.id,
        GrAppv=50000.0,
        Term=60.0,
        State="CA",
        NAICS_Sectors="44",
        New="Yes",
        Franchise="0",
        NoEmp=10,
        RevLineCr="Yes",
        LowDoc="No",
        Rural="No",
        prediction=True
    )
    session.add(loan)
    session.commit()
    session.refresh(loan)
    return loan