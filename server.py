from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from collections import deque
import os
import json

app = FastAPI()

# rooms: room_id -> set(websockets)
rooms = {}

# history: room_id -> deque(сообщений), максимум 100
history = {}

@app.get("/")
async def get():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(base_dir, "client.html"))

@app.get("/video")
async def get_video():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(base_dir, "video.mp4"), media_type="video/mp4")

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    if room_id not in rooms:
        rooms[room_id] = set()
    if room_id not in history:
        history[room_id] = deque(maxlen=100)

    rooms[room_id].add(websocket)
    print(f"🔵 Подключение: {room_id}. Всего комнат: {list(rooms.keys())}")

    # Отправляем новому участнику историю чата
    if history[room_id]:
        history_msg = json.dumps({
            "action": "chatHistory",
            "messages": list(history[room_id])
        })
        await websocket.send_text(history_msg)
        print(f"📜 Отправлена история ({len(history[room_id])} сообщений) в {room_id}")

    try:
        while True:
            data = await websocket.receive_text()

            try:
                parsed = json.loads(data)
                if parsed.get("action") == "chat":
                    history[room_id].append(parsed)
            except Exception:
                pass

            for client in list(rooms[room_id]):
                await client.send_text(data)
    except WebSocketDisconnect:
        rooms[room_id].remove(websocket)
        print(f"🔴 Отключение: {room_id}. Осталось: {len(rooms[room_id])}")
        if not rooms[room_id]:
            del rooms[room_id]
