## **File Structure**

```bash
fastapi_mysql_project/
│
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & routes
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic models
│   ├── database.py      # DB connection
│   ├── auth.py          # JWT authentication
│   └── crud.py          # Database operations
│
├── requirements.txt
├── .env                 # Environment variables
└── README.md
```

---

## **Step-by-Step Setup**

### **1. Create Project Structure**

Run these commands in your terminal:

# Create virtual environment

    bash

            python -m venv venv
            source venv/bin/activate # Linux/Mac

     venv\Scripts\activate # Windows

```bash
# Create project folder
mkdir fastapi_mysql_project
cd fastapi_mysql_project

# Create app structure
mkdir app
touch app/__init__.py
touch app/{main.py,models.py,schemas.py,database.py,auth.py,crud.py}

# Create supporting files
touch requirements.txt .env README.md
```

---

### **2. Install Dependencies**

Add these to `requirements.txt`:

```text
fastapi
uvicorn
python-jose[cryptography]
passlib[bcrypt]
pymysql
sqlalchemy
python-dotenv
```

Then install them:

```bash
pip install -r requirements.txt
```

view list of installing depedency

```bash
pip list
```

---

Here's a breakdown of each dependency in your FastAPI project and why it's used:

### 1. **`fastapi`**

**Purpose**: The main web framework for building your API  
**Why it's needed**:

- Provides tools to create RESTful APIs quickly
- Automatic API documentation (Swagger UI & ReDoc)
- Data validation using Pydantic models
- Dependency injection system
- ASGI support for high performance
- Handles HTTP requests and responses

### 2. **`uvicorn`**

**Purpose**: ASGI server to run your FastAPI application  
**Why it's needed**:

- Serves your FastAPI application in production
- Supports async/await functionality
- Provides hot reload during development (`--reload` flag)
- Lightweight and fast implementation of ASGI specification

### 3. **`python-jose[cryptography]`**

**Purpose**: JWT (JSON Web Token) implementation  
**Why it's needed**:

- Creates and verifies JWT tokens for authentication
- `[cryptography]` adds support for cryptographic operations
- Used in your `auth.py` for:
  - `create_access_token()` - Generating tokens
  - `decode_token()` - Verifying tokens
- Implements industry-standard JWT (RFC 7519)

### 4. **`passlib[bcrypt]`**

**Purpose**: Password hashing library  
**Why it's needed**:

- Securely hashes passwords before storing in database
- `[bcrypt]` provides the bcrypt hashing algorithm (industry standard)
- Used in `auth.py` for:
  - `get_password_hash()` - Hashing passwords during registration
  - `verify_password()` - Checking passwords during login
- Protects against rainbow table attacks

### 5. **`pymysql`**

**Purpose**: MySQL database connector  
**Why it's needed**:

- Enables Python to communicate with MySQL/MariaDB
- Used by SQLAlchemy as the database driver
- Provides the `mysql+pymysql://` connection string in `database.py`
- Handles low-level database protocol communication

### 6. **`sqlalchemy`**

**Purpose**: ORM (Object-Relational Mapper) for databases  
**Why it's needed**:

- Allows defining database models as Python classes (`models.py`)
- Manages database sessions and connections
- Provides:
  - `declarative_base()` for model definitions
  - `SessionLocal` for database sessions
  - Query building interface
- Abstracts away raw SQL queries

### 7. **`python-dotenv`**

**Purpose**: Environment variable management  
**Why it's needed**:

- Loads variables from `.env` file into application
- Keeps sensitive data (database credentials, secrets) out of code
- Used in `database.py` and `auth.py` to access:
  - Database connection strings
  - JWT secret keys
  - Algorithm configurations

### How They Work Together:

1. **FastAPI** handles HTTP requests and routes them to your functions
2. **SQLAlchemy** + **PyMySQL** talk to your MySQL database
3. **Passlib** secures user passwords
4. **python-jose** manages authentication tokens
5. **Uvicorn** serves the entire application
6. **python-dotenv** keeps configurations secure

### **3. Configure MySQL Database**

#### **a) Update `.env`**

```text
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=fastapi_todo
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
```

#### **b) Set Up `database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, bind=engine)
Base = declarative_base()
```

---

### **4. Define Models (`models.py`)**

```python
from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(String(500))
    completed = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    password = Column(String(100))  # Hashed
```

---

### **5. Pydantic Schemas (`schemas.py`)**

```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False

class UserCreate(BaseModel):
    username: str
    password: str
```

---

### **6. Auth Logic (`auth.py`)**

```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expires})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
```

---

### **7. CRUD Operations (`crud.py`)**

```python
from sqlalchemy.orm import Session
from . import models, schemas

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session):
    return db.query(models.Task).all()

# Add more CRUD functions (get_task, update_task, delete_task)
```

---

### **8. FastAPI App (`main.py`)**

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, auth
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Task Routes
@app.post("/tasks/")
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)

@app.get("/tasks/")
def read_tasks(db: Session = Depends(get_db)):
    return crud.get_tasks(db)

# Auth Routes
@app.post("/register/")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    return {"message": "User created"}

@app.post("/token/")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}
```

---

### **9. Run the Application**

```bash
uvicorn app.main:app --reload
```

- Access Swagger UI: `http://localhost:8000/docs`
- Test endpoints:
  - `POST /tasks/`
  - `GET /tasks/`
  - `POST /register/`
  - `POST /token/`

---

## **Key Features Implemented**

✅ **Structured project** (models, schemas, routes separated)  
✅ **MySQL integration** (SQLAlchemy)  
✅ **JWT Authentication** (register/login)  
✅ **Environment variables** (`.env`)

---

````markdown
# FastAPI MySQL Todo Application

A complete FastAPI application with MySQL integration, JWT authentication, and CRUD operations for tasks.

## Project Structure

```bash
fastapi_mysql_project/
│
├── app/
│   ├── __init__.py         # Makes app a Python package
│   ├── main.py             # FastAPI app & routes
│   ├── models.py           # SQLAlchemy database models
│   ├── schemas.py          # Pydantic models for request/response
│   ├── database.py         # Database connection setup
│   ├── auth.py             # JWT authentication logic
│   └── crud.py             # Database operations
│
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── README.md               # Project documentation
```
````

## File Explanations

### 1. `database.py`

- Sets up the MySQL database connection using SQLAlchemy
- Creates the database engine and session factory
- Uses environment variables from `.env` for configuration

### 2. `models.py`

- Defines SQLAlchemy models for database tables:
  - `Task`: Stores task information (id, title, description, completed)
  - `User`: Stores user credentials (id, username, hashed password)

### 3. `schemas.py`

- Pydantic models for data validation:
  - `TaskCreate`: Schema for creating/updating tasks
  - `UserCreate`: Schema for user registration

### 4. `auth.py`

- Handles JWT authentication:
  - Password hashing with bcrypt
  - Token creation and verification
  - Uses environment variables for secret key

### 5. `crud.py`

- Contains database operations:
  - `create_task`: Adds new tasks to database
  - `get_tasks`: Retrieves all tasks

### 6. `main.py`

- FastAPI application entry point:
  - Creates database tables on startup
  - Defines API routes:
    - Task CRUD endpoints
    - User registration/login endpoints
  - Uses dependency injection for database sessions

## Workflow

1. **Setup**:

   - Create MySQL database (`fastapi_todo`)
   - Configure `.env` with database credentials
   - Install dependencies with `pip install -r requirements.txt`

2. **Running**:

   ```bash
   uvicorn app.main:app --reload
   ```

   Access Swagger UI at: `http://localhost:8000/docs`

3. **API Endpoints**:

### Authentication

- `POST /register/`: Register new user

  ```json
  {
    "username": "testuser",
    "password": "test123"
  }
  ```

- `POST /token/`: Login and get JWT token
  ```json
  {
    "username": "testuser",
    "password": "test123"
  }
  ```

### Tasks (Require JWT Auth)

- `POST /tasks/`: Create new task

  ```json
  {
    "title": "Learn FastAPI",
    "description": "Build a CRUD API",
    "completed": false
  }
  ```

- `GET /tasks/`: Get all tasks

## Database Schema

### Users Table

| Column   | Type    | Description     |
| -------- | ------- | --------------- |
| id       | Integer | Primary key     |
| username | String  | Unique username |
| password | String  | Hashed password |

### Tasks Table

| Column      | Type    | Description       |
| ----------- | ------- | ----------------- |
| id          | Integer | Primary key       |
| title       | String  | Task title        |
| description | String  | Task description  |
| completed   | Boolean | Completion status |

## Environment Variables

Create `.env` file with:

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=fastapi_todo
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
```

## Dependencies

- FastAPI
- Uvicorn
- SQLAlchemy
- PyMySQL
- Python-JOSE (JWT)
- Passlib (Password hashing)
- python-dotenv

```

This README provides:
1. Clear project structure explanation
2. File-by-file documentation
3. API usage examples
4. Database schema details
5. Environment setup guide
6. Workflow instructions

```
