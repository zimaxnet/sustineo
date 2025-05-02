from functools import partial
from typing import Any, Callable, Union, get_type_hints
from api.agent.model import Agent
from prompty.utils import get_json_type


function_agents: dict[str, Agent] = {}
function_calls: dict[str, Agent] = {}


def agent(func: Union[Callable, None] = None, **kwargs: Any) -> Callable:
    global function_agents

    if func is None:
        return partial(agent, **kwargs)

    if "description" not in kwargs:
        return func

    if "name" not in kwargs:
        return func

    name = kwargs.pop("name")
    description = kwargs.pop("description")
    args = get_type_hints(func, include_extras=True)

    # remove the return and notify arguments from the args dictionary
    args.pop("return", None)
    args.pop("notify", None)

    if func.__name__ not in function_agents:
        function_agents[name.lower().replace(" ", "_")] = Agent(
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
                if (k != "return" or k != "notify")
            ],
        )

    return func


async def get_function_agents() -> dict[str, Agent]:
    global function_agents
    return function_agents
