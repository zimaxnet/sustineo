import typing
import prompty
from fastapi import APIRouter
from pydantic import BaseModel
from .common import (
    get_foundry_agents,
    Agent,
    get_custom_agents,
    custom_agents,
    foundry_agents,
)
from ..connection import connections

# from api.connection import connections

# available agents
router = APIRouter(
    prefix="/api/agent",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
    dependencies=[],
)


@router.get("/refresh")
async def refresh_agents():
    # reload agents from prompty files in directory
    await get_custom_agents()
    return {"message": "Agents refreshed"}


@router.get("/")
async def get_agents():
    if not custom_agents:
        await get_custom_agents()
    # return list of available agents
    a = [
        Agent(
            id=agent.id,
            name=agent.name,
            type=agent.model.connection["type"],
            description=agent.description,
            options=agent.model.options,
            parameters=[
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                }
                for param in agent.inputs
            ],
        )
        for agent in custom_agents.values()
    ]
    agents = await get_foundry_agents()
    f = [
        Agent(
            id=agent.id,
            name=agent.name,
            type=agent.type,
            description=agent.description,
            parameters=[
                {
                    "name": param["name"],
                    "type": param["type"],
                    "description": param["description"],
                    "required": param["required"],
                }
                for param in agent.parameters
            ],
        )
        for agent in agents.values()
    ]

    return [*f, *a]


@router.get("/{id}")
async def get_agent(id: str):
    # return agent by id
    if id not in custom_agents:
        return {"error": "Agent not found"}

    return {k: v for k, v in custom_agents[id].to_safe_dict().items() if k != "file"}


class FunctionCall(BaseModel):
    call_id: str
    id: str
    name: str
    arguments: dict[str, typing.Any]


@router.post("/{id}")
async def execute_agent(id: str, function: FunctionCall):

    if id in connections:
        await connections.send_message(
            id,
            "agent",
            {
                "name": function.name,
                "call_id": function.call_id,
                "message": "Starting agent execution",
            },
        )

        if function.name in custom_agents:
            # execute custom prompty agent
            agent = custom_agents[function.name]
            result = await prompty.execute_async(
                agent,
                inputs={**function.arguments},
            )

            await connections.send_message(
                id,
                "agent",
                {
                    "name": function.name,
                    "call_id": function.call_id,
                    "message": "Agent execution completed",
                    "result": result,
                },
            )

            return {
                "status": "success",
            }

        if function.name in foundry_agents:
            # execute foundry agent
            foundry_agent = foundry_agents[function.name]
            await connections.send_message(
                id,
                "agent",
                {
                    "name": function.name,
                    "message": "Starting agent execution",
                    "call_id": function.call_id,
                    "agentId": foundry_agent.id,
                    "agentName": foundry_agent.name,
                },
            )

        return {"status": "success"}
