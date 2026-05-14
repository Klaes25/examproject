from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
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
    allow_origins=[
        "http://localhost:18765",
        "http://127.0.0.1:18765",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    username: str
    password: str


def ensure_admin_user():
    db: Session = SessionLocal()

    admin_user = db.query(User).filter(
        User.username == "admin"
    ).first()

    if not admin_user:
        hashed_password = pwd_context.hash("admin")

        new_admin = User(
            username="admin",
            password_hash=hashed_password
        )

        db.add(new_admin)
        db.commit()

    db.close()


ensure_admin_user()


@app.get("/")
def root():
    return FileResponse("/frontend/index.html")


@app.post("/register")
def register(data: LoginRequest):
    raise HTTPException(status_code=403, detail="Registration is disabled")


@app.post("/login")
def login(data: LoginRequest):
    db: Session = SessionLocal()

    user = db.query(User).filter(
        User.username == data.username
    ).first()

    if not user:
        db.close()
        raise HTTPException(status_code=401, detail="Forkert login")

    if not pwd_context.verify(data.password, user.password_hash):
        db.close()
        raise HTTPException(status_code=401, detail="Forkert login")

    db.close()

    return {
        "message": "Login successful",
        "username": data.username
    }

@app.websocket("/ws/control")
async def websocket_control(websocket: WebSocket):
    await websocket.accept()
    print("Browser connected to /ws/control")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Command received: {data}")
            await websocket.send_text(f"Server received: {data}")

    except WebSocketDisconnect:
        print("Browser disconnected from /ws/control")
