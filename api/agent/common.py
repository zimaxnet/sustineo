import os
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient


FOUNDRY_CONNECTION = os.environ.get("FOUNDRY_CONNECTION", "EMPTY")

async def get_foundry_agents():

    project = AIProjectClient.from_connection_string(
        conn_str=FOUNDRY_CONNECTION, credential=DefaultAzureCredential()
    )

    agents = await project.agents.list_agents()


    await project.close()
    return [
        {
            "id": agent["id"],
            "name": agent["name"],
            "type": "foundry-agent",
            "description": agent["description"],
            "options": {
                "agent_id": agent["id"],
            },
        }
        for agent in agents.data
    ]
