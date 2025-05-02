import json
from functools import partial
from typing import Any, Callable, Union, get_type_hints
from prompty.utils import get_json_type

def agent(func: Union[Callable, None] = None, **kwargs: Any) -> Callable:
    if func is None:
        return partial(agent, **kwargs)

    if "description" not in kwargs:
        raise ValueError("The 'description' argument is required.")

    if "name" not in kwargs:
        raise ValueError("The 'name' argument is required.")

    name = kwargs.pop("name")
    description = kwargs.pop("description")
    args = get_type_hints(func, include_extras=True)


    

    metadata = {
        "id": func.__name__,
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": {
                k: {
                    "type": get_json_type(v.__args__[0]),
                    "description": (
                        v.__metadata__[0]
                        if hasattr(v, "__metadata__")
                        else "No Description"
                    ),
                }
                for k, v in args.items()
            },
        },
    }
    print(json.dumps(metadata, indent=2))
    return func
