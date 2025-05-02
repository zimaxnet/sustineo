import base64
import os
from typing import Annotated
import aiohttp
from pathlib import Path
import uuid
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

BASE_PATH = Path(__file__).resolve(strict=True).parent

AZURE_IMAGE_ENDPOINT = os.environ.get("AZURE_IMAGE_ENDPOINT", "EMPTY").rstrip("/")
AZURE_IMAGE_API_KEY = os.environ.get("AZURE_IMAGE_API_KEY", "EMPTY")
SUSTINEO_STORAGE = os.environ.get("SUSTINEO_STORAGE", "EMPTY")


async def gpt_image_generation(
    prompt: Annotated[
        str,
        "The prompt to generate the image, be as descriptive as possible to get the best results",
    ],
    n: Annotated[int, "number of images to generate"] = 1,
) -> list[str]:

    size: str = "1024x1024"
    quality: str = "medium"
    api_version = "2025-04-01-preview"
    deployment_name = "gpt-image-1"
    endpoint = f"{AZURE_IMAGE_ENDPOINT}/openai/deployments/{deployment_name}/images/generations?api-version={api_version}"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            endpoint,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {AZURE_IMAGE_API_KEY}",
            },
            json={
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "output_compression": 100,
                "output_format": "png",
                "n": n,
            },
        ) as response:
            if response.status != 200:
                print(f"Error: {response.status}")
                return []

            image = await response.json()
            # save the image to a file
            # iterate through the images and save them
            if not image["data"]:
                print("No images found in the response.")
                return []

            imgs = {}
            for item in image["data"]:
                if item["b64_json"]:
                    base_64image = item["b64_json"]
                    image_bytes = base64.b64decode(base_64image)
                    imgs[str(uuid.uuid4())] = image_bytes

            return await save_to_storage(imgs, "images")


async def save_to_storage(images: dict[str, bytes], folder_name: str) -> list[str]:
    imgs = []
    async with DefaultAzureCredential() as credential:
        async with BlobServiceClient(
            account_url=SUSTINEO_STORAGE, credential=credential
        ) as blob_service_client:
            container_client = blob_service_client.get_container_client("sustineo")
            # Create the container if it doesn't exist
            if not await container_client.exists():
                await container_client.create_container()

            for image_name, image in images.items():
                blob_name = f"{folder_name}/{image_name}.png"
                await container_client.upload_blob(
                    name=blob_name, data=image, overwrite=True
                )

                imgs.append(blob_name)
    return imgs


if __name__ == "__main__":
    import asyncio
    import time

    start_time = time.time()

    prompt = "Visualize the step-by-step process of making a backstitch with a simple explanation under each image. create this in the style of war posters from world war ii in britain"
    img = asyncio.run(gpt_image_generation(prompt, 3))
    print(f"Image generated and saved to {img}")
    print(f"Time taken: {time.time() - start_time} seconds")
