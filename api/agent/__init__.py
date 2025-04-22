from fastapi import APIRouter
from pathlib import Path
import prompty
from prompty.core import Prompty

# from api.connection import connections

# available agents
agents: dict[str, Prompty] = {}


# load agents from prompty files in directory
async def load_agents():
    agents_dir = Path(__file__).parent
    for agent_file in agents_dir.glob("*.prompty"):
        agent_name = agent_file.stem
        prompty_agent = await prompty.load_async(str(agent_file))
        agents[prompty_agent.id] = prompty_agent
        print(f"Loaded agent: {agent_name}")


router = APIRouter(
    prefix="/api/agent",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
    dependencies=[],
)


@router.get("/")
async def get_agents():
    # return list of available agents
    return {
        "agents": [
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "model": {
                    "api": agent.model.api,
                    "connection": agent.model.connection,
                    "options": agent.model.options,
                },
                "inputs": agent.inputs,
            }
            for agent in agents.values()
        ]
    }


@router.get("/{id}")
async def get_agent(id: str):
    # return agent by id
    if id not in agents:
        return {"error": "Agent not found"}

    return {k: v for k, v in agents[id].to_safe_dict().items() if k != "file"}


@router.post("/{id}")
async def execute_agent(id: str, input: str):
    # execute agent by id
    if id not in agents:
        return {"error": "Agent not found"}

    agent = agents[id]
    result = await prompty.execute_async(
        agent,
        inputs={"input": input},
    )
    return result
