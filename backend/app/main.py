from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal, engine
from app.models import Base, User

import json
import os
import secrets
import time

Base.metadata.create_all(bind=engine)

app = FastAPI()

active_tokens = set()
ROVER_TOKEN = os.getenv("ROVER_TOKEN")


def require_user_token(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authentication token")

    token = authorization.replace("Bearer ", "", 1).strip()

    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Invalid authentication token")


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

    connected = (
        rover_websocket is not None
        and last_seen is not None
        and now - last_seen < 15
    )

    return {
        **latest_rover_status,
        "connected": connected,
        "seconds_since_last_seen": None if last_seen is None else round(now - last_seen, 1)
    }

@app.get("/api/sensor-data")
def get_sensor_data(_: None = Depends(require_user_token)):
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT id, temperature, humidity, distance, created_at
            FROM sensor_data
            ORDER BY created_at DESC
            LIMIT 50
        """)).fetchall()

        return [
            {
                "id": row[0],
                "temperature": row[1],
                "humidity": row[2],
                "distance": row[3],
                "created_at": str(row[4])
            }
            for row in rows
        ]

    finally:
        db.close()



@app.get("/api/detections")
def get_detections(_: None = Depends(require_user_token)):
    db = SessionLocal()

    try:
        rows = db.execute(text("""
            SELECT id, object_name, color, confidence, image_path, created_at
            FROM detections
            ORDER BY created_at DESC
            LIMIT 20
        """)).fetchall()

        return [
            {
                "id": row[0],
                "object_name": row[1],
                "color": row[2],
                "confidence": row[3],
                "image_path": row[4],
                "created_at": str(row[5])
            }
            for row in rows
        ]

    finally:
        db.close()


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

    token = secrets.token_urlsafe(32)
    active_tokens.add(token)

    return {
        "message": "Login successful",
        "username": data.username,
        "token": token
    }


@app.websocket("/ws/control")
async def websocket_control(websocket: WebSocket):
    global rover_websocket

    token = websocket.query_params.get("token")

    if token not in active_tokens:
        await websocket.close(code=1008)
        print("Rejected browser WebSocket connection without valid user token")
        return

    await websocket.accept()
    print("Browser/operator connected to /ws/control")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Control data received: {data}")

            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
                continue

            message_type = parsed.get("type")

            if message_type in ["drive", "arm", "stop"]:
                if rover_websocket is None:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No rover connected"
                    })
                    continue

                try:
                    await rover_websocket.send_json(parsed)
                    await websocket.send_json({
                        "type": "ack",
                        "message": "Command forwarded to rover",
                        "data": parsed
                    })
                except Exception as error:
                    print(f"Failed to forward command to rover: {error}")
                    rover_websocket = None
                    latest_rover_status["connected"] = False
                    latest_rover_status["status"] = "offline"

                    await websocket.send_json({
                        "type": "error",
                        "message": "Failed to forward command to rover"
                    })

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "Control endpoint only accepts drive, arm and stop messages",
                    "data": parsed
                })

    except WebSocketDisconnect:
        print("Browser/operator disconnected from /ws/control")


async def handle_rover_message(websocket: WebSocket, parsed: dict, raw_data: str):
    message_type = parsed.get("type")

    if message_type == "status":
        latest_rover_status["connected"] = True
        latest_rover_status["status"] = parsed.get("status")
        latest_rover_status["device"] = parsed.get("device")
        latest_rover_status["last_seen"] = time.time()
        latest_rover_status["last_message"] = parsed

        db = SessionLocal()

        try:
            db.execute(
                text("""
                INSERT INTO logs (
                    level,
                    source,
                    message
                )
                VALUES (
                    :level,
                    :source,
                    :message
                )
                """),
                {
                    "level": "INFO",
                    "source": "rover",
                    "message": (
                        f"Rover status update: "
                        f"status={parsed.get('status')}, "
                        f"device={parsed.get('device')}"
                    )
                }
            )
            db.commit()

        finally:
            db.close()

        await websocket.send_json({
            "type": "ack",
            "message": "Server received rover status",
            "data": parsed
        })

    elif message_type == "sensor_data":
        latest_rover_status["connected"] = True
        latest_rover_status["last_seen"] = time.time()
        latest_rover_status["last_message"] = parsed

        temperature = parsed.get("temperature")
        humidity = parsed.get("humidity")
        distance = parsed.get("distance")

        db = SessionLocal()

        try:
            db.execute(
                text("""
                INSERT INTO sensor_data (
                    temperature,
                    humidity,
                    distance
                )
                VALUES (
                    :temperature,
                    :humidity,
                    :distance
                )
                """),
                {
                    "temperature": temperature,
                    "humidity": humidity,
                    "distance": distance
                }
            )
            db.commit()

        finally:
            db.close()

        print("Sensor data:", parsed)

        await websocket.send_json({
            "type": "ack",
            "message": "Server received sensor data",
            "data": parsed
        })

    elif message_type == "detection":

        object_name = parsed.get("object") or parsed.get("object_name")

        if object_name is None:
            print("Detection ignored: object missing")
            await websocket.send_json({
                "type": "error",
                "message": "Detection ignored: object missing",
                "data": parsed
            })

        else:
            latest_rover_status["connected"] = True
            latest_rover_status["last_seen"] = time.time()
            latest_rover_status["last_message"] = parsed

            db = SessionLocal()

            try:
                db.execute(
                    text("""
                    INSERT INTO detections (
                        object_name,
                        color,
                        confidence,
                        image_path
                    )
                    VALUES (
                        :object_name,
                        :color,
                        :confidence,
                        :image_path
                    )
                    """),
                    {
                        "object_name": object_name,
                        "color": parsed.get("color"),
                        "confidence": parsed.get("confidence"),
                        "image_path": parsed.get("image_path")
                    }
                )
                db.commit()

            finally:
                db.close()

            print("Detection data:", parsed)

            await websocket.send_json({
                "type": "ack",
                "message": "Server received detection data",
                "data": parsed
            })

    else:
        await websocket.send_json({
            "type": "error",
            "message": "Unknown rover message type",
            "data": parsed
        })

@app.websocket("/ws/rover")
async def websocket_rover(websocket: WebSocket):
    global rover_websocket

    token = websocket.query_params.get("token")

    if not ROVER_TOKEN or token != ROVER_TOKEN:
        await websocket.close(code=1008)
        print("Rejected rover WebSocket connection without valid rover token")
        return

    await websocket.accept()
    rover_websocket = websocket

    latest_rover_status["connected"] = True
    latest_rover_status["status"] = "online"
    latest_rover_status["device"] = "raspberry_pi_rover"
    latest_rover_status["last_seen"] = time.time()

    print("Rover connected to /ws/rover")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Rover data received: {data}")

            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
                continue

            await handle_rover_message(websocket, parsed, data)

    except WebSocketDisconnect:
        print("Rover disconnected from /ws/rover")

        if websocket == rover_websocket:
            rover_websocket = None
            latest_rover_status["connected"] = False
            latest_rover_status["status"] = "offline"
