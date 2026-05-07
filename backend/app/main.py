from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, User

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="/frontend"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:18888"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/")
def root():
    return FileResponse("/frontend/index.html")


@app.post("/register")
def register(data: LoginRequest):
    db: Session = SessionLocal()

    existing_user = db.query(User).filter(
        User.username == data.username
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(data.password)

    new_user = User(
        username=data.username,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()

    return {"message": "User created"}


@app.post("/login")
def login(data: LoginRequest):
    db: Session = SessionLocal()

    user = db.query(User).filter(
        User.username == data.username
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Forkert login..")

    if not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Forkert login..")

    return {"message": "Login sucess"}
