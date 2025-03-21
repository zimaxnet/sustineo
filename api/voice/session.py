import json
from typing import Literal, Union
from fastapi import WebSocket
from prompty.tracer import trace
from fastapi import WebSocketDisconnect
from pydantic import BaseModel
from prompty.tracer import Tracer
from fastapi.websockets import WebSocketState


from api.voice.realtime import RealtimeVoiceClient


class Message(BaseModel):
    type: Literal["user", "assistant", "audio", "console", "interrupt", "messages"]
    payload: str


class RealtimeSession:

    def __init__(self, realtime: RealtimeVoiceClient, client: WebSocket):
        self.realtime: Union[RealtimeVoiceClient, None] = realtime
        self.client: Union[WebSocket, None] = client

    async def send_message(self, message: Message):
        if self.client is not None:
            await self.client.send_json(message.model_dump())

    async def send_audio(self, audio: Message):
        # send audio to client, format into bytes
        if self.client is not None:
            await self.client.send_json(audio.model_dump())

    async def send_console(self, message: Message):
        if self.client is not None:
            await self.client.send_json(message.model_dump())

    async def send_realtime_instructions(
        self,
        instructions: Union[str | None] = None,
        threshold: float = 0.8,
        silence_duration_ms: int = 500,
        prefix_padding_ms: int = 300,
    ):
        if self.realtime is not None:
            await self.realtime.send_session_update(
                instructions, threshold, silence_duration_ms, prefix_padding_ms
            )

    @trace
    async def receive_realtime(self):
        signature = "api.session.RealtimeSession.receive_realtime"
        while self.realtime is not None and not self.realtime.closed:
            async for message in self.realtime.receive_message():
                # print("received message", message.type)
                if message is None:
                    continue

                match message.type:
                    case "session.created":
                        with Tracer.start("session_created") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(Tracer.INPUTS, message.content)
                            await self.send_console(
                                Message(
                                    type="console", payload=json.dumps(message.content)
                                )
                            )
                    case "conversation.item.input_audio_transcription.completed":
                        with Tracer.start("receive_user_transcript") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(
                                Tracer.INPUTS,
                                {
                                    "type": "conversation.item.input_audio_transcription.completed",
                                    "role": "user",
                                    "content": message.content,
                                },
                            )
                            if (
                                message.content is not None
                                and isinstance(message.content, str)
                                and message.content != ""
                            ):
                                await self.send_message(
                                    Message(type="user", payload=message.content)
                                )

                    case "response.audio_transcript.done":
                        with Tracer.start("receive_assistant_transcript") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(
                                Tracer.INPUTS,
                                {
                                    "type": "response.audio_transcript.done",
                                    "role": "assistant",
                                    "content": message.content,
                                },
                            )
                            if (
                                message.content is not None
                                and isinstance(message.content, str)
                                and message.content != ""
                            ):
                                # audio stream
                                await self.send_message(
                                    Message(type="assistant", payload=message.content)
                                )

                    case "response.audio.delta":
                        if (
                            message.content is not None
                            and isinstance(message.content, str)
                            and message.content != ""
                        ):
                            await self.send_audio(
                                Message(type="audio", payload=message.content)
                            )

                    case "response.failed":
                        with Tracer.start("realtime_failure") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(
                                Tracer.INPUTS,
                                {
                                    "failure": message.content,
                                },
                            )
                            print("Realtime failure", message.content)

                    case "turn_detected":
                        # send interrupt message
                        with Tracer.start("turn_detected") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(
                                Tracer.INPUTS,
                                {
                                    "type": "turn_detected",
                                    "content": message.content,
                                },
                            )
                            await self.send_console(
                                Message(type="interrupt", payload="")
                            )
                    case _:
                        with Tracer.start("unhandled_message") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(
                                Tracer.INPUTS,
                                {
                                    "type": "unhandled_message",
                                    "content": message.content,
                                },
                            )
                            await self.send_console(
                                Message(type="console", payload="Unhandled message")
                            )

        self.realtime = None

    @trace
    async def receive_client(self):
        signature = "api.session.RealtimeSession.receive_client"
        if self.client is None or self.realtime is None:
            return
        try:
            while self.client.client_state != WebSocketState.DISCONNECTED:
                message = await self.client.receive_text()

                message_json = json.loads(message)
                m = Message(**message_json)
                # print("received message", m.type)
                match m.type:
                    case "audio":
                        await self.realtime.send_audio_message(m.payload)
                    case "user":
                        with Tracer.start("user_message") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(Tracer.INPUTS, m.model_dump())
                            await self.realtime.send_user_message(m.payload)
                    case "interrupt":
                        with Tracer.start("trigger_response") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(Tracer.INPUTS, m.model_dump())
                            await self.realtime.trigger_response()
                    case _:
                        with Tracer.start("user_message") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(Tracer.INPUTS, m.model_dump())
                            await self.send_console(
                                Message(type="console", payload="Unhandled message")
                            )
        except WebSocketDisconnect:
            print("Realtime Socket Disconnected")

    async def close(self):
        if self.client is None or self.realtime is None:
            return
        try:
            await self.client.close()
            await self.realtime.close()
        except Exception as e:
            print("Error closing session", e)
            self.client = None
            self.realtime = None

