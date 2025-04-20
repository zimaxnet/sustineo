import os
import json
import asyncio
from pathlib import Path
from openai import AsyncAzureOpenAI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from api.voice.common import get_default_configuration_data
from api.voice.session import Message, RealtimeSession
from api.voice.configuration import router as voice_configuration_router

from dotenv import load_dotenv

load_dotenv()

AZURE_VOICE_ENDPOINT = os.getenv("AZURE_VOICE_ENDPOINT") or ""
AZURE_VOICE_KEY = os.getenv("AZURE_VOICE_KEY", "fake_key")
LOCAL_TRACING_ENABLED = os.getenv("LOCAL_TRACING_ENABLED", "false").lower() == "true"
COSMOSDB_CONNECTION = os.getenv("COSMOSDB_CONNECTION", "fake_connection")

base_path = Path(__file__).parent

connections: dict[str, WebSocket] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # manage lifetime scope
        yield
    finally:
        # remove all stray sockets
        for connection in connections.values():
            await connection.close()
        connections.clear()


app = FastAPI(lifespan=lifespan)

app.include_router(voice_configuration_router, tags=["voice"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimpleMessage(BaseModel):
    name: str
    text: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/api/message")
async def message(message: SimpleMessage):
    return {"message": f"Hello {message.name}, you sent: {message.text}"}


@app.websocket("/api/voice/{id}")
async def voice_endpoint(id: str, websocket: WebSocket):
    # check if the connection is already open
    if id in connections:
        await connections[id].close()
        del connections[id]

    connections[id] = websocket
    # accept the connection
    await websocket.accept()
    try:
        client = AsyncAzureOpenAI(
            azure_endpoint=AZURE_VOICE_ENDPOINT,
            api_key=AZURE_VOICE_KEY,
            api_version="2024-10-01-preview",
        )
        async with client.beta.realtime.connect(
            model="gpt-4o-realtime-preview",
        ) as realtime_client:

            # get current username and receive any parameters
            user_message = await websocket.receive_json()
            user = Message(**user_message)

            settings = json.loads(user.payload)
            print(
                "Starting voice session with settings:\n",
                json.dumps(settings, indent=2),
            )

            # create voice system message
            customer = settings["user"] if "user" in settings else "unnamed user"
            prompt_settings = await get_default_configuration_data(customer=customer)
            if prompt_settings is None:
                await websocket.send_json(
                    {
                        "error": "No default configuration found.",
                        "message": "Please contact support.",
                    }
                )
                await websocket.close()
                return

            session = RealtimeSession(
                realtime=realtime_client,
                client=websocket,
            )

            await session.update_realtime_session(
                instructions=prompt_settings.system_message,
                threshold=settings["threshold"] if "threshold" in settings else 0.8,
                silence_duration_ms=(
                    settings["silence"] if "silence" in settings else 500
                ),
                prefix_padding_ms=(settings["prefix"] if "prefix" in settings else 300),
                tools=prompt_settings.tools,
            )

            tasks = [
                asyncio.create_task(session.receive_realtime()),
                asyncio.create_task(session.receive_client()),
            ]
            await asyncio.gather(*tasks)

    except WebSocketDisconnect as e:
        if id in connections:
            del connections[id]
        print("Voice Socket Disconnected", e)
