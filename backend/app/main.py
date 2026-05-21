from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, User

import json
import time

Base.metadata.create_all(bind=engine)

app = FastAPI()

latest_rover_status = {
    "connected": False,
    "status": "unknown",
    "device": None,
    "last_seen": None,
    "last_message": None
}

rover_websocket = None

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


@app.get("/")
def root():
    return FileResponse("/frontend/index.html")


@app.get("/api/rover/status")
def get_rover_status():
    now = time.time()
    last_seen = latest_rover_status["last_seen"]

    connected = False

    if last_seen is not None and now - last_seen < 15:
        connected = True

    return {
        **latest_rover_status,
        "connected": connected,
        "seconds_since_last_seen": None if last_seen is None else round(now - last_seen, 1)
    }


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
    global rover_websocket

    await websocket.accept()
    print("Client connected to /ws/control")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Data received: {data}")

            try:
                parsed = json.loads(data)

                if parsed.get("type") == "status":
                    rover_websocket = websocket

                    latest_rover_status["connected"] = True
                    latest_rover_status["status"] = parsed.get("status")
                    latest_rover_status["device"] = parsed.get("device")
                    latest_rover_status["last_seen"] = time.time()
                    latest_rover_status["last_message"] = parsed

                    await websocket.send_json({
                        "type": "ack",
                        "message": "Server received data",
                        "data": data
                    })

                elif parsed.get("type") == "sensor_data":
                    latest_rover_status["last_seen"] = time.time()
                    latest_rover_status["last_message"] = parsed

                    print("Sensor data:", parsed)

                    await websocket.send_json({
                        "type": "ack",
                        "message": "Server received data",
                        "data": data
                    })

                elif parsed.get("type") in ["drive", "arm", "stop"]:
                    if rover_websocket is not None:
                        await rover_websocket.send_json(parsed)

                        await websocket.send_json({
                            "type": "ack",
                            "message": "Server received data",
                            "data": data
                        })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No rover connected"
                        })

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Unknown message type",
                        "data": parsed
                    })

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        print("Client disconnected from /ws/control")

        if websocket == rover_websocket:
            rover_websocket = None
            latest_rover_status["connected"] = False
            latest_rover_status["status"] = "offline"
