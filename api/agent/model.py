from dataclasses import dataclass, field
from typing import Any, Literal, Optional
from pydantic import BaseModel


class FunctionCall(BaseModel):
    call_id: str
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class Agent:
    id: str
    name: str
    type: str
    description: str
    parameters: list[dict[str, Any]]
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentStatus:
    id: str
    agentName: str
    callId: str
    name: Literal["run", "step", "message"]
    status: str
    type: Optional[str] = field(default=None)
    content: Optional[dict[str, Any]] = field(default=None)
