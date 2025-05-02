import os
import contextlib
from pathlib import Path
from functools import partial
from typing import Any, Callable, Coroutine, Union, get_type_hints

import prompty
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    MessageInputContentBlock,
    MessageAttachment,
)

from azure.identity.aio import DefaultAzureCredential
from prompty.core import Prompty

from prompty.utils import get_json_type
from api.agent.model import Agent, AgentStatus
from api.agent.handler import SustineoAgentEventHandler


FOUNDRY_CONNECTION = os.environ.get("FOUNDRY_CONNECTION", "EMPTY")
foundry_agents: dict[str, Agent] = {}
custom_agents: dict[str, Prompty] = {}
function_agents: dict[str, Agent] = {}
function_calls: dict[str, Agent] = {}


def agent(func: Union[Callable, None] = None, **kwargs: Any) -> Callable:
    if func is None:
        return partial(agent, **kwargs)

    if "description" not in kwargs:
        return func

    if "name" not in kwargs:
        return func

    name = kwargs.pop("name")
    description = kwargs.pop("description")
    args = get_type_hints(func, include_extras=True)

    if func.__name__ not in function_agents:
        function_agents[func.__name__] = Agent(
            id=func.__name__,
            name=name,
            type="function_agent",
            description=description,
            parameters=[
                {
                    "name": k,
                    "type": get_json_type(v.__args__[0]),
                    "description": (
                        v.__metadata__[0]
                        if hasattr(v, "__metadata__")
                        else "No Description"
                    ),
                    "required": True,
                }
                for k, v in args.items()
            ],
        )


    return func


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


async def create_foundry_thread():
    """Create a Foundry thread."""
    async with get_foundry_project_client() as project_client:
        thread = await project_client.agents.create_thread()
        return thread.id


async def create_thread_message(
    thread_id: str,
    role: str,
    content: Union[str, list[MessageInputContentBlock]],
    attachments: list[MessageAttachment] = [],
    metadata: dict[str, str] = {},
):
    """Create a Foundry message."""
    async with get_foundry_project_client() as project_client:
        message = await project_client.agents.create_message(
            thread_id=thread_id,
            role=role,
            content=content,
            metadata=metadata,
            attachments=attachments,
        )
        return message.id