import os
import uuid
import aiohttp
import base64
from typing import Annotated, Any, Callable, Coroutine, Literal, Optional
from api.agent.decorators import agent
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient


AZURE_IMAGE_ENDPOINT = os.environ.get("AZURE_IMAGE_ENDPOINT", "EMPTY").rstrip("/")
AZURE_IMAGE_API_KEY = os.environ.get("AZURE_IMAGE_API_KEY", "EMPTY")
SUSTINEO_STORAGE = os.environ.get("SUSTINEO_STORAGE", "EMPTY")


@agent(
    name="GPT-image-1 Agent",
    description="This agent can generate a number of images based upon a detailed description. This agent is based on the GPT-Image-1 model and is capable of generating images in a variety of styles. It can also generate images in a specific style, such as a painting or a photograph. The agent can also generate images with different levels of detail and complexity.",
)
async def gpt_image_generation(
    description: Annotated[
        str,
        "The detailed description of the image to be generated. The more detailed the description, the better the image will be. Make sure to include the style of the image, the colors, and any other details that will help the model generate a better image.",
    ],
    n: Annotated[int, "number of images to generate"],
    notify: Callable[
        [
            Literal["run", "step", "message"],
            Literal["in_progress", "failed", "completed"],
            str,
            Optional[dict[str, Any]],
        ],
        Coroutine[Any, Any, Any],
    ],
):

    await notify(
        "run",
        "in_progress",
        "image_generation",
        {"message": "Starting image generation"},
    )

    size: str = "1024x1024"
    quality: str = "medium"
    api_version = "2025-04-01-preview"
    deployment_name = "gpt-image-1"
    endpoint = f"{AZURE_IMAGE_ENDPOINT}/openai/deployments/{deployment_name}/images/generations?api-version={api_version}"

    await notify(
        "step",
        "in_progress",
        "image_generation",
        {"message": "Executing Model"},
    )
    async with aiohttp.ClientSession() as session:
        async with session.post(
            endpoint,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {AZURE_IMAGE_API_KEY}",
            },
            json={
                "prompt": description,
                "size": size,
                "quality": quality,
                "output_compression": 100,
                "output_format": "png",
                "n": n,
            },
        ) as response:
            if response.status != 200:
                print(f"Error: {response.status}")
                await notify(
                    "run",
                    "failed",
                    "image_generation",
                    {"message": f"Error: {response.status}"},
                )
                return []

            await notify(
                "step",
                "in_progress",
                "image_generation",
                {"message": "fetching images" if n > 1 else "fetching image"},
            )
            image = await response.json()
            # save the image to a file
            # iterate through the images and save them
            if not image["data"]:
                print("No images found in the response.")
                return []

            await notify(
                "step",
                "in_progress",
                "image_generation",
                {"message": "storing images" if n > 1 else "storing image"},
            )
            async with DefaultAzureCredential() as credential:
                async with BlobServiceClient(
                    account_url=SUSTINEO_STORAGE, credential=credential
                ) as blob_service_client:
                    container_client = blob_service_client.get_container_client(
                        "sustineo"
                    )
                    # Create the container if it doesn't exist
                    if not await container_client.exists():
                        await container_client.create_container()

                    images = []
                    for item in image["data"]:
                        if item["b64_json"]:
                            base_64image = item["b64_json"]
                            image_bytes = base64.b64decode(base_64image)
                            blob_name = f"images/{str(uuid.uuid4())}.png"
                            await container_client.upload_blob(
                                name=blob_name, data=image_bytes, overwrite=True
                            )

                            await notify(
                                "step",
                                "completed",
                                "image_generation",
                                {
                                    "message": "Image generated successfully",
                                    "description": description,
                                    "size": size,
                                    "quality": quality,
                                    "image_url": blob_name,
                                },
                            )

                            images.append(blob_name)
                    await notify(
                        "run",
                        "completed",
                        "image_generation",
                        {
                            "message": "Image generation complete",
                            "images": images,
                        },
                    )
                    return images
