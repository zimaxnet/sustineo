from dataclasses import dataclass
import os
from pathlib import Path
from typing import Union
from prompty.utils import parse
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, ContainerProxy
import aiofiles
import contextlib

COSMOSDB_CONNECTION = os.getenv("COSMOSDB_CONNECTION", "fake_connection")
DATABASE_NAME = "sustineo"
CONTAINER_NAME = "VoiceConfigurations"


@dataclass
class Configuration:
    id: str
    name: str
    default: bool
    content: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "default": self.default,
            "content": self.content,
        }


async def seed_configurations(container: ContainerProxy) -> list[Configuration]:
    configs = []
    # Load default configuration from file
    config = await load_prompty_file("voice.prompty")
    if config:
        await container.upsert_item(
            {
                "id": config.id,
                "name": config.name,
                "default": config.default,
                "content": config.content,
            }
        )
        configs.append(config)

    config = await load_prompty_file("travel.prompty", True)
    if config:
        await container.upsert_item(
            {
                "id": config.id,
                "name": config.name,
                "default": config.default,
                "content": config.content,
            }
        )
        configs.append(config)

    return configs


def load_prompty(contents: str, default: bool = False) -> Configuration:
    matter = parse(contents)
    atttributes = matter.pop("attributes", {})
    config = Configuration(
        id=atttributes.get("id", "default"),
        name=atttributes.get("name", "Default"),
        default=default,
        content=contents,
    )
    return config


async def load_prompty_file(
    prompty: str, default: bool = False
) -> Union[Configuration, None]:
    file = Path(__file__).parent / prompty
    config = None
    try:
        async with aiofiles.open(file, "r", encoding="utf-8") as f:
            file_content = await f.read()

        config = load_prompty(file_content, default=default)
    except Exception as e:
        print(f"Error loading default configuration: {e}")
    finally:
        return config


@contextlib.asynccontextmanager
async def get_cosmos_container():
    # Create a Cosmos DB client
    client = CosmosClient.from_connection_string(COSMOSDB_CONNECTION)
    database = await client.create_database_if_not_exists(DATABASE_NAME)
    container = await database.create_container_if_not_exists(
        id=CONTAINER_NAME,
        partition_key=PartitionKey(path="/id"),
        offer_throughput=400,
    )
    try:
        yield container
    finally:
        await client.close()
