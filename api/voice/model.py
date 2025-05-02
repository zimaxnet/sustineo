from dataclasses import dataclass, field
from typing import Any, Optional
from pydantic import BaseModel
from openai.types.beta.realtime.session_update_event import SessionTool


class Config(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    default: Optional[bool] = False
    tools: Optional[list[dict]] = None
    content: str


@dataclass
class Configuration:
    id: str
    name: str
    default: bool
    content: str
    tools: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "default": self.default,
            "content": self.content,
        }


@dataclass
class DefaultConfiguration:
    system_message: str
    tools: list[SessionTool]
