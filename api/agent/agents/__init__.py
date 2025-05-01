from typing import Annotated


async def annotated_function(
    name: Annotated[str, "this is the name of the customer"],
    age: Annotated[int, "this is the age of the customer"],
) -> Annotated[str, "this is the return type of the function"]:
    """
    This function takes a name and age as input and returns a formatted string.

    Args:
        name (str): The name of the person.
        age (int): The age of the person.

    Returns:
        str: A formatted string with the name and age.
    """
    
    return f"{name} is {age} years old."


if __name__ == "__main__":
    print(annotated_function("John", 30))
    print(annotated_function.__annotations__)
