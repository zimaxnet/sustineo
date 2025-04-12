import os
import json
import asyncio
from pathlib import Path
from typing import Optional
from openai import AsyncAzureOpenAI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from jinja2 import Environment, FileSystemLoader
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from api.voice.configuration import VoiceConfiguration
from api.voice.session import Message, RealtimeSession

from dotenv import load_dotenv

load_dotenv()

AZURE_VOICE_ENDPOINT = os.getenv("AZURE_VOICE_ENDPOINT") or ""
AZURE_VOICE_KEY = os.getenv("AZURE_VOICE_KEY", "fake_key")
LOCAL_TRACING_ENABLED = os.getenv("LOCAL_TRACING_ENABLED", "false").lower() == "true"
COSMOSDB_CONNECTION = os.getenv("COSMOSDB_CONNECTION", "fake_connection")

base_path = Path(__file__).parent

# jinja2 template environment
env = Environment(loader=FileSystemLoader(base_path / "voice"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # manage lifetime scope
        yield
    finally:
        # remove all stray sockets
        pass


app = FastAPI(lifespan=lifespan)

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

class Configuration(BaseModel):
    id: Optional[str] = None
    content: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/api/message")
async def message(message: SimpleMessage):
    return {"message": f"Hello {message.name}, you sent: {message.text}"}


@app.get("/api/configurations")
async def configurations():
    configs = VoiceConfiguration(
        connection_string=COSMOSDB_CONNECTION
    )

    return await configs.get_configurations()

@app.put("/api/configuration")
async def configuration(configuration: Configuration):
    configs = VoiceConfiguration(
        connection_string=COSMOSDB_CONNECTION
    )

    await configs.upsert_configuration(configuration.content, configuration.id)

    return {"message": "Configuration updated"}



@app.websocket("/api/voice")
async def voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket.
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
            system_message = env.get_template("script.jinja2").render(
                customer=settings["user"] if "user" in settings else "unnamed user"
            )

            session = RealtimeSession(
                realtime=realtime_client,
                client=websocket,
            )

            await session.update_realtime_session(
                system_message,
                threshold=settings["threshold"] if "threshold" in settings else 0.8,
                silence_duration_ms=(
                    settings["silence"] if "silence" in settings else 500
                ),
                prefix_padding_ms=(settings["prefix"] if "prefix" in settings else 300),
                customer=settings["user"] if "user" in settings else "Seth",
            )

            tasks = [
                asyncio.create_task(session.receive_realtime()),
                asyncio.create_task(session.receive_client()),
            ]
            await asyncio.gather(*tasks)

    except WebSocketDisconnect as e:
        print("Voice Socket Disconnected", e)
