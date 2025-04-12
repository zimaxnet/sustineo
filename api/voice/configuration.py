from dataclasses import dataclass
from pathlib import Path
from typing import Union
from prompty.utils import parse
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, ContainerProxy
import aiofiles
import contextlib


@dataclass
class Configuration:
    id: str
    name: str
    default: bool
    content: str


def load_prompty(contents: str) -> Configuration:
    matter = parse(contents)
    atttributes = matter.pop("attributes", {})
    config = Configuration(
        id=atttributes.get("id", "default"),
        name=atttributes.get("name", "Default"),
        default=True,
        content=contents,
    )
    return config


class VoiceConfiguration:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.database_name = "sustineo"
        self.container_name = "VoiceConfigurations"

    @contextlib.asynccontextmanager
    async def _get_container(self):
        # Create a Cosmos DB client
        client = CosmosClient.from_connection_string(self.connection_string)
        database = await client.create_database_if_not_exists(self.database_name)
        container = await database.create_container_if_not_exists(
            id=self.container_name,
            partition_key=PartitionKey(path="/id"),
            offer_throughput=400,
        )
        try:
            yield container
        finally:
            await client.close()

    async def load_default(
        self, prompty: str, container: ContainerProxy, default: bool = False
    ):
        # Load default configuration from file
        file = Path(__file__).parent / prompty
        try:
            async with aiofiles.open(file, "r", encoding="utf-8") as f:
                file_content = await f.read()

            config = load_prompty(file_content)
            config.default = default
            # Store as default configuration
            await container.create_item(
                {
                    "id": config.id,
                    "name": config.name,
                    "default": config.default,
                    "content": config.content,
                }
            )

            return config

        except Exception as e:
            print(f"Error loading default configuration: {e}")

    async def get_configurations(self):
        async with self._get_container() as container:
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
                # Load default configuration if none exists
                config = await self.load_default("voice.prompty", container)
                if config:
                    configurations.append(config)

                config = await self.load_default("travel.prompty", container, True)
                if config:
                    configurations.append(config)

        return configurations

    async def upsert_configuration(
        self, configuration: str, id: Union[str, None] = None
    ) -> Configuration:
        async with self._get_container() as container:
            config = load_prompty(configuration)

            if id:
                await container.delete_item(item=id, partition_key=id)

            # Upsert the configuration
            item = await container.upsert_item(
                {
                    "id": config.id,
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

    async def delete_configuration(self, id: str) -> bool:
        async with self._get_container() as container:
            try:
                await container.delete_item(id, partition_key=id)
                return True
            except Exception as e:
                print(f"Error deleting configuration: {e}")
                return False

    async def set_default_configuration(self, id: str) -> bool:
        async with self._get_container() as container:
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
