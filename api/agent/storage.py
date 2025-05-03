import os
import contextlib
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient


SUSTINEO_STORAGE = os.environ.get("SUSTINEO_STORAGE", "EMPTY")

@contextlib.asynccontextmanager
async def get_storage_client(container: str):
    # Create credential and blob service client
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
        account_url=SUSTINEO_STORAGE, credential=credential
    )
    try:
        # Create the container if it doesn't exist
        container_client = blob_service_client.get_container_client(container)
        if not await container_client.exists():
            await container_client.create_container()
            
        yield container_client
    finally:
        await credential.close()
        await blob_service_client.close()
