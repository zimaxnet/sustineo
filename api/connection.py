import json
from typing import Any, Literal, TypeAlias
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from pydantic import BaseModel


MessageType: TypeAlias = Literal[
    "user", "assistant", "system", "audio", "console", "interrupt", "function", "agent"
]

class Message(BaseModel):
    type: MessageType
    payload: str


class Connection:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def send_text(self, message: str):
        await self.websocket.send_text(message)

    async def receive_json(self) -> dict:
        return await self.websocket.receive_json()

    async def send_json(self, message: dict):
        await self.websocket.send_json(message)

    async def accept(self):
        await self.websocket.accept()

    async def receive_text(self) -> str:
        return await self.websocket.receive_text()

    async def send_message(self, message: Message):
        await self.websocket.send_json(message.model_dump())

    async def send_audio(self, audio: Message):
        await self.websocket.send_json(audio.model_dump())

    async def send_console(self, message: Message):
        await self.websocket.send_json(message.model_dump())

    async def close(self):
        if self.websocket.client_state == WebSocketState.CONNECTED:
            await self.websocket.close()

    @property
    def state(self) -> WebSocketState:
        return self.websocket.client_state


# class for managing websocket connections by id
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, Connection] = {}

    async def connect(self, id: str, websocket: WebSocket) -> Connection:
        # destroy existing connection if it exists
        if id in self.active_connections:
            await self.active_connections[id].close()
            del self.active_connections[id]

        await websocket.accept()
        self.active_connections[id] = Connection(websocket)
        return self.active_connections[id]

    async def send_message(self, id: str, type: MessageType, payload: dict[str, Any]):
        if id in self.active_connections:
            await self.active_connections[id].send_message(Message(type=type, payload=json.dumps(payload)))
        else:
            raise ValueError(f"Connection with id {id} not found.")


    def __getitem__(self, id: str) -> Connection:
        if id not in self.active_connections:
            raise KeyError(f"Connection with id {id} not found.")
        return self.active_connections[id]

    def __contains__(self, id: str) -> bool:
        return id in self.active_connections

    async def clear(self):
        keys = list(self.active_connections.keys())
        for key in keys:
            await self.active_connections[key].close()
            del self.active_connections[key]

    def remove(self, id: str):
        if id in self.active_connections:
            del self.active_connections[id]


connections = ConnectionManager()