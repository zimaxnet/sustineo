from api.agent.model import Agent, AgentStatus
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    AsyncAgentEventHandler,
    RunStep,
    ThreadMessage,
    ThreadRun,
)
from typing import Any, Callable, Coroutine, Union


class SustineoAgentEventHandler(AsyncAgentEventHandler[str]):

    def __init__(
        self,
        project_client: AIProjectClient,
        agent: Agent,
        call_id: str,
        notify: Callable[[AgentStatus], Coroutine[Any, Any, Any]],
    ) -> None:
        super().__init__()
        self.project_client = project_client
        self.agent = agent
        self.notify = notify
        self.call_id = call_id
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

        if isinstance(message, ThreadRun):
            await self.notify(
                AgentStatus(
                    id=message.id,
                    agentName=self.agent.name,
                    callId=self.call_id,
                    name="run",
                    status=message.status,
                )
            )
        elif isinstance(message, RunStep):
            if message.status == "completed" and message.type != "message_creation":
                await self.notify(
                    AgentStatus(
                        id=message.id,
                        agentName=self.agent.name,
                        callId=self.call_id,
                        name="step",
                        status="completed",
                        type=message.type,
                        content=message.step_details.as_dict(),
                    )
                )
            else:
                await self.notify(
                    AgentStatus(
                        id=message.id,
                        agentName=self.agent.name,
                        callId=self.call_id,
                        name="step",
                        status=message.status,
                        type=message.type,
                    )
                )
        elif isinstance(message, ThreadMessage):
            if message.status == "completed":
                await self.notify(
                    AgentStatus(
                        id=message.id,
                        agentName=self.agent.name,
                        callId=self.call_id,
                        name="message",
                        status="completed",
                        type="thread_message",
                        content={
                            "type": "thread_message",
                            "thread_message": [m.as_dict() for m in message.content],
                        },
                    )
                )
            else:
                await self.notify(
                    AgentStatus(
                        id=message.id,
                        agentName=self.agent.name,
                        callId=self.call_id,
                        name="message",
                        status=message.status,
                    )
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
