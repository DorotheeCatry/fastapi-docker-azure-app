# 🚀 Loan Eligibility Prediction API with FastAPI

A **FastAPI** project that exposes a classification model to predict loan eligibility while ensuring data security through robust authentication.

## 🔥 Objectives

- 🏦 **Expose a prediction model** to evaluate loan eligibility.
- 🔒 **Ensure API security** via JWT authentication.
- 📊 **Record all requests** in a database for analysis.
- 🔑 **Allow users to change their password** after the first login.

---

## 🛠 Technologies Used

| Component         | Technology |
|------------------|------------|
| **Language**     | Python     |
| **Framework**    | FastAPI    |
| **Database**     | SQLModel (SQLAlchemy + Pydantic) |
| **Authentication** | JWT (JSON Web Token) with OAuth2 |

---

## 📂 Project Structure

```
project/
│-- app/
│   │-- core/               # Configuration & security
│   │-- db/                 # Database & sessions
│   │-- models/             # SQLModel models
│   │-- schemas/            # Pydantic schemas for validation
│   │-- api/                # API routes (auth, users, loans)
│   │   │-- v1/             # API versioning
│   │       │-- endpoints/  # Endpoints
│   │-- utils/              # Utility functions (JWT, hash...)
│   │-- main.py             # FastAPI entry point
│__ requirements.txt        # Dependencies
```

---

## 🔑 Authentication & Security

- 🔐 **Password hashing and salting** using Passlib (bcrypt).
- 🕒 **JWT token expiration** for enhanced security.
- 👤 **Role-based permission management** (Admin, User).

---

## 📌 Features & Endpoints

| Method | URL | Description | Access |
|--------|----------------|--------------------------------|-------------|
| **POST** | `/auth/login` | Login & retrieve token | All |
| **POST** | `/auth/activation` | Account activation & password change | User |
| **POST** | `/auth/logout` | Logout | User |
| **GET** | `/loans/predict` | Loan eligibility prediction | User |
| **POST** | `/loans/request` | Submit a loan request | User |
| **GET** | `/loans/history` | Loan request history | User |
| **GET** | `/admin/users` | List all users | Admin |
| **POST** | `/admin/users` | Create a new user | Admin |

---

## 🗄 Database Model

### 🔹 Table `users`
Stores user information:
- Email
- Hashed password
- Role (Admin, User)
- Activation status

### 🔹 Table `LoanRequests`
Stores loan requests with:
- Requester's ID
- Request status
- Associated details

---

## 🚀 Installation & Deployment

### 1️⃣ Clone the repository
```bash
git clone https://github.com/DorotheeCatry/fastapi-docker-azure-app.git
cd fastapi-loan-api
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Apply migrations
```bash
alembic upgrade head
```

### 4️⃣ Run the server
```bash
uvicorn app.main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000` 🚀.

---

## 📌 Testing

To run unit tests:
```bash
pytest
```

---

## 📜 License
Open-source project under the **MIT** license.

