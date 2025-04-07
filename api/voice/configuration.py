from dataclasses import dataclass
from pathlib import Path
from prompty.utils import parse
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, ContainerProxy
import aiofiles


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
        content=contents
    )
    return config

class VoiceConfiguration:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.database_name = "sustineo"
        self.container_name = "VoiceConfigurations"


    async def load_default(self, container: ContainerProxy):
        file = Path(__file__).parent / "voice.prompty"
        try:
            async with aiofiles.open(file, 'r', encoding='utf-8') as f:
                file_content = await f.read()

            config = load_prompty(file_content)
            # Store as default configuration
            await container.create_item({
                'id': config.id,
                'name': config.name,
                'default': config.default,
                'content': config.content
            })

            return config

        except Exception as e:
            print(f"Error loading default configuration: {e}")

    async def get_configurations(self):
        client = CosmosClient.from_connection_string(self.connection_string)
        database = await client.create_database_if_not_exists("VoiceConfiguration")
        container = await database.create_container_if_not_exists(
            id=self.container_name,
            partition_key=PartitionKey(path="/id"),
            offer_throughput=400
        )


        items = container.read_all_items()
        configurations = []
        async for item in items:
            configurations.append(Configuration(
                id=item['id'],
                name=item['name'],
                default=item['default'],
                content=item['content']
            ))

        if len(configurations) == 0:
            # Load default configuration if none exists
            config = await self.load_default(container)

            print("No configurations found.")
            return [config]
        
        await client.close()

        return configurations
