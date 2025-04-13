from fastapi import APIRouter
from pydantic import BaseModel

from api.voice.data import (
    Configuration,
    get_cosmos_container,
    load_prompty,
    seed_configurations,
)


router = APIRouter(
    prefix="/api/configuration",
    tags=["voice"],
    responses={404: {"description": "Not found"}},
    dependencies=[],
)


class Config(BaseModel):
    content: str


@router.get("/")
async def get_configurations():
    async with get_cosmos_container() as container:
        items = container.read_all_items()
        configurations: list[Configuration] = []
        async for item in items:
            configurations.append(
                Configuration(
                    id=item["id"],
                    name=item["name"],
                    default=item["default"],
                    content=item["content"],
                )
            )

        if len(configurations) == 0:
            configurations = await seed_configurations(container)

    return configurations


@router.get("/{id}")
async def get_configuration(id: str):
    async with get_cosmos_container() as container:
        try:
            item = await container.read_item(item=id, partition_key=id)
            return Configuration(
                id=item["id"],
                name=item["name"],
                default=item["default"],
                content=item["content"],
            )
        except Exception as e:
            print(f"Error getting configuration: {e}")
            return {}


@router.post("/")
async def upsert_configuration(configuration: Config) -> Configuration:
    async with get_cosmos_container() as container:
        config = load_prompty(configuration.content)

        try:
            # Upsert the configuration
            item = await container.create_item(
                {
                    "id": config.id,
                    "name": config.name,
                    "default": False,
                    "content": config.content,
                }
            )
            return Configuration(
                id=item["id"],
                name=item["name"],
                default=item["default"],
                content=item["content"],
            )
        except Exception as e:
            print(f"Error upserting configuration: {e}")
            return Configuration(
                id=config.id,
                name="Error",
                default=False,
                content=str(e),
            )


@router.put("/{id}")
async def update_configuration(id: str, configuration: Config) -> Configuration:
    async with get_cosmos_container() as container:
        config = load_prompty(configuration.content)

        # Update the configuration
        item = await container.upsert_item(
            {
                "id": id,
                "name": config.name,
                "content": config.content,
            }
        )

        return Configuration(
            id=item["id"],
            name=item["name"],
            default=item["default"],
            content=item["content"],
        )


@router.delete("/{id}")
async def delete_configuration(id: str) -> bool:
    async with get_cosmos_container() as container:
        try:
            await container.delete_item(id, partition_key=id)
            return True
        except Exception as e:
            print(f"Error deleting configuration: {e}")
            return False


@router.put("/default/{id}")
async def set_default_configuration(id: str) -> bool:
    async with get_cosmos_container() as container:
        try:
            # set all other configurations to not default
            items = container.read_all_items()
            async for item in items:
                if item["id"] != id:
                    item["default"] = False
                    await container.upsert_item(item)
                else:
                    item["default"] = True
                    await container.upsert_item(item)
            return True
        except Exception as e:
            print(f"Error setting default configuration: {e}")
            return False
