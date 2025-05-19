import os
from azure.ai.resources.agents import AgentsClient, ToolSet
from azure.ai.resources.agents.tools import FileSearchTool
from azure.ai.resources.entities import FilePurpose
from azure.identity import DefaultAzureCredential

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
    version="latest",
)

with agents_client:
    conn_id = os.environ["AZURE_AI_CONNECTION_ID"]

    file = agents_client.upload_file_and_poll(
        file_path=asset_file_path, purpose=FilePurpose.AGENTS
    )

    vector_store = agents_client.create_vector_store_and_poll(
        file_ids=[file.id], name="rsvp_vector_store"
    )

    file_search = FileSearchTool(vector_store_ids=[vector_store.id])
    toolset = ToolSet()
    toolset.add(file_search)

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="RSVP Agent",
        instructions=(
            "RSVP Agent: Invite attendees, create events, and track responses.\n\n"
            "1. Use File Search tool to resolve invitees.\n"
            "2. Invite all contacts if no names are given.\n"
            "3. Ask for event details if missing (today is May 20, 2025).\n"
            "4. Use resolved contacts to create and send calendar invites."
        ),
        toolset=toolset,
    )

    print(f"Agent created: {agent.id}")
