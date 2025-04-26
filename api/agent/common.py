import os
import typing
from pathlib import Path
import prompty
from prompty.core import Prompty
from dataclasses import dataclass, field
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient


@dataclass
class Agent:
    id: str
    name: str
    type: str
    description: str
    parameters: list[dict[str, typing.Any]]
    options: dict[str, typing.Any] = field(default_factory=dict)


FOUNDRY_CONNECTION = os.environ.get("FOUNDRY_CONNECTION", "EMPTY")
foundry_agents: dict[str, Agent] = {}
custom_agents: dict[str, Prompty] = {}


# load agents from prompty files in directory
async def get_custom_agents():
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


async def get_foundry_agents() -> dict[str, Agent]:

    project = AIProjectClient.from_connection_string(
        conn_str=FOUNDRY_CONNECTION, credential=DefaultAzureCredential()
    )

    agents = await project.agents.list_agents()

    await project.close()
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
