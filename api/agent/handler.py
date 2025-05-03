from typing import Any, Union

from azure.ai.projects.models import (
    AsyncAgentEventHandler,
    RunStep,
    ThreadMessage,
    ThreadRun,
)
from api.model import AgentUpdateEvent, Content


class SustineoAgentEventHandler(AsyncAgentEventHandler[str]):

    def __init__(
        self,
        notify: AgentUpdateEvent,
    ) -> None:
        super().__init__()
        self.notify = notify
        self.history: list[dict[str, Any]] = []

    async def add_message(
        self,
        message: Union[ThreadMessage, ThreadRun, RunStep],
    ) -> None:
        last_message = self.history[-1] if self.history else None
        # if the last message is the same as the current one, skip it
        # this is to avoid duplicate messages in the history
        if (
            last_message
            and last_message["id"] == message["id"]
            and last_message["status"] == message["status"]
            and last_message["object"] == message["object"]
        ):
            return

        status = message["status"].replace("_", " ")

        if isinstance(message, ThreadRun):
            await self.notify(
                id=message.id,
                status=f"run {status}",
            )

        elif isinstance(message, RunStep):

            type = message["type"].replace("_", " ")
            if message.status == "completed" and message.type == "tool_calls":
                tool_calls: list[dict[str, Any]] = message.step_details.as_dict()[
                    "tool_calls"
                ]

                items = [
                    {
                        "id": tool_call["id"],
                        "type": tool_call["type"],
                        **{
                            key: value
                            for key, value in tool_call[tool_call["type"]].items()
                        },
                    }
                    for tool_call in tool_calls
                ]

                await self.notify(
                    id=message.id,
                    status=f"step \"{type}\" {status}",
                    content=Content(type="tool_calls", content=items),
                )
            else:
                await self.notify(
                    id=message.id,
                    status=f"step \"{type}\" {status}",
                )
        elif isinstance(message, ThreadMessage):
            if message.status == "completed":
                text: list[dict[str, Any]] = [m.as_dict() for m in message.content]
                items = [
                    {
                        "type": m["type"],
                        **m[m["type"]],
                    }
                    for m in text
                ]

                await self.notify(
                    id=message.id,
                    status=f"message {status}",
                    information="Acquired Result",
                    content=Content(type="text", content=items),
                    output=True,
                )

            else:
                await self.notify(
                    id=message.id,
                    status=f"message {status}",
                )

        self.history.append(message.as_dict())

    async def on_thread_message(self, message: "ThreadMessage") -> None:
        await self.add_message(message)

    async def on_thread_run(self, run: "ThreadRun") -> None:
        await self.add_message(run)

    async def on_run_step(self, step: "RunStep") -> None:
        await self.add_message(step)

    async def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")
