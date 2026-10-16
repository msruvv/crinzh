from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Храним подключения по комнатам
rooms = {}  # room_id -> set(websockets)

@app.get("/")
async def get():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(base_dir, "client.html"))

# ← И ЭТОТ ТОЖЕ
@app.get("/video")
async def get_video():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(base_dir, "video.mp4"), media_type="video/mp4")

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    if room_id not in rooms:
        rooms[room_id] = set()
    rooms[room_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            for client in list(rooms[room_id]):
                await client.send_text(data)
    except WebSocketDisconnect:
        rooms[room_id].remove(websocket)
        if not rooms[room_id]:
            del rooms[room_id]