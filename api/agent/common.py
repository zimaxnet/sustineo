import json
import os
import contextlib
from pathlib import Path
from typing import Any, Callable, Coroutine, Union

import prompty
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    AsyncAgentEventHandler,
    RunStep,
    ThreadMessage,
    ThreadRun,
)
from azure.identity.aio import DefaultAzureCredential
from prompty.core import Prompty

from api.agent.model import Agent, AgentStatus


FOUNDRY_CONNECTION = os.environ.get("FOUNDRY_CONNECTION", "EMPTY")
foundry_agents: dict[str, Agent] = {}
custom_agents: dict[str, Prompty] = {}


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
                        }
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


# load agents from prompty files in directory
async def get_custom_agents() -> dict[str, Prompty]:
    global custom_agents
    agents_dir = Path(__file__).parent / "agents"
    if not agents_dir.exists():
        print(f"Agents directory does not exist: {agents_dir}")
        return {}

    custom_agents.clear()
    for agent_file in agents_dir.glob("*.prompty"):
        agent_name = agent_file.stem
        prompty_agent = await prompty.load_async(str(agent_file))
        custom_agents[prompty_agent.id] = prompty_agent
        print(f"Loaded agent: {agent_name}")

    return custom_agents


@contextlib.asynccontextmanager
async def get_foundry_project_client():
    """Get a context manager for the Foundry project client."""
    creds = DefaultAzureCredential()
    project_client = AIProjectClient.from_connection_string(
        conn_str=FOUNDRY_CONNECTION, credential=creds
    )
    try:
        yield project_client
    finally:
        await creds.close()
        await project_client.close()


async def get_foundry_agents() -> dict[str, Agent]:
    global foundry_agents
    async with get_foundry_project_client() as project_client:
        agents = await project_client.agents.list_agents()
        foundry_agents = {
            agent["name"]
            .strip()
            .replace(" ", "_")
            .lower(): Agent(
                id=agent["id"],
                name=agent["name"],
                type="foundry-agent",
                description=agent["description"],
                parameters=[
                    {
                        "name": "additional_instructions",
                        "type": "string",
                        "description": f"Additional instructions for the \"{agent['name']}\" agent. Provide additional instructions for the system message of the agent to fulfill the task with the following description: {agent['description']}",
                        "required": True,
                    },
                    {
                        "name": "query",
                        "type": "string",
                        "description": f"Query for the \"{agent['name']}\" agent. Provide enough context to fulfill the task with the following description: {agent['description']}. Provide the query to the agent as if you were talking to it.",
                        "required": True,
                    },
                ],
            )
            for agent in agents.data
        }

        return foundry_agents


async def execute_foundry_agent(
    agent: Agent,
    additional_instructions: str,
    query: str,
    call_id: str,
    notify: Callable[[AgentStatus], Coroutine[Any, Any, Any]],
):
    """Execute a Foundry agent."""

    async with get_foundry_project_client() as project_client:
        server_agent = await project_client.agents.get_agent(agent.id)
        thread = await project_client.agents.create_thread()
        await project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=query,
        )

        handler = SustineoAgentEventHandler(project_client, agent, call_id, notify)
        async with await project_client.agents.create_stream(
            agent_id=server_agent.id,
            thread_id=thread.id,
            additional_instructions=additional_instructions,
            event_handler=handler,
        ) as stream:
            await stream.until_done()


if __name__ == "__main__":
    import asyncio

    agents = asyncio.run(get_foundry_agents())
    print("Foundry agents loaded successfully.")

    agent = agents["bing_search_agent"]
    instr = "This agent can use the web to find information on current winter camping trends in 2025, especially related to tents and outdoor gear. The search results should return any relevant insights or popular practices."
    query = "winter camping trends 2025 tents outdoor gear"
    # instr = "This agent can use the web to find information on the Azure AI Foundry Agent Service. The search results should return any relevant insights or popular practices."
    # query = "latest news Azure AI Foundry Agent Service"

    async def notify(status: AgentStatus):
        print(f"{json.dumps(status.__dict__, indent=2)}")

    asyncio.run(
        execute_foundry_agent(
            agent=agent,
            additional_instructions=instr,
            query=query,
            call_id="12345",
            notify=notify,
        )
    )
    print("Agent executed successfully.")
