import json
from typing import Any, Callable, Coroutine, Literal, Optional
import uuid
from fastapi import APIRouter

from api.agent.decorators import function_agents
from api.agent.model import AgentStatus, FunctionCall
from api.agent.common import (
    get_foundry_agents,
    get_custom_agents,
    custom_agents,
    foundry_agents,
)
from api.agent.model import Agent
from api.agent.common import execute_foundry_agent

# load function agents
import api.agent.agents as agents  # noqa: F401

from api.connection import connections

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
    global connections, custom_agents, foundry_agents, function_agents
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

    return [*f, *a, *function_agents.values()]


@router.get("/{id}")
async def get_agent(id: str):
    global connections, custom_agents, foundry_agents
    # return agent by id
    if id not in custom_agents:
        return {"error": "Agent not found"}

    return {k: v for k, v in custom_agents[id].to_safe_dict().items() if k != "file"}


def send_agent_status(id: str) -> Callable[[AgentStatus], Coroutine[Any, Any, Any]]:
    global connections

    async def status_fn(status: AgentStatus):
        # send agent status to connection
        if id in connections:
            await connections[id].send_json(
                {
                    "type": "agent",
                    "payload": json.dumps(
                        {
                            "id": status.id,
                            "agentName": status.agentName,
                            "callId": status.callId,
                            "name": status.name,
                            "status": status.status,
                            "type": status.type,
                            "content": status.content,
                        }
                    ),
                }
            )

    return status_fn


def send_func_agent_status(
    id: str,
    call_id: str,
    agent_ref: Agent,
) -> Callable[
    [
        Literal["run", "step", "message"],
        Literal["in_progress", "failed", "completed"],
        str,
        Optional[dict[str, Any]],
    ],
    Coroutine[Any, Any, Any],
]:
    global connections

    async def status_fn(
        name: Literal["run", "step", "message"],
        status: Literal["in_progress", "failed", "completed"],
        type: str,
        content: Optional[dict[str, Any]] = None,
    ):
        # send agent status to connection
        if id in connections:
            await connections[id].send_json(
                {
                    "type": "agent",
                    "payload": json.dumps(
                        {
                            "id": str(uuid.uuid4()).replace("-", ""),
                            "agentName": agent_ref.name,
                            "callId": call_id,
                            "name": name,
                            "status": status,
                            "type": type,
                            "content": content,
                        }
                    ),
                }
            )

    return status_fn


@router.post("/{id}")
async def execute_agent(id: str, function: FunctionCall):
    global connections, custom_agents, foundry_agents, function_agents

    if len(foundry_agents) == 0:
        foundry_agents = await get_foundry_agents()

    if id not in connections:
        return {"error": "Connection not found"}

    if function.name in foundry_agents:
        # execute foundry agent
        foundry_agent = foundry_agents[function.name]
        await execute_foundry_agent(
            foundry_agent,
            function.arguments["additional_instructions"],
            function.arguments["query"],
            function.call_id,
            send_agent_status(id),
        )
    elif function.name in function_agents:
        function_agent = function_agents[function.name]
        functions = dir(agents)
        if function_agent.id in functions:
            # execute function agent
            func = getattr(agents, function_agent.id)
            args = function.arguments.copy()
            args["notify"] = send_func_agent_status(
                id,
                function.call_id,
                function_agent,
            )
            await func(**args)
        else:
            return {"error": "Function not found"}
