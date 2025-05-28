import os
from typing import Annotated
from api.agent.decorators import agent

from api.model import AgentUpdateEvent, Content
from api.agent.storage import save_image_blobs
from api.agent.common import execute_foundry_agent, post_request


AZURE_IMAGE_ENDPOINT = os.environ.get("AZURE_IMAGE_ENDPOINT", "EMPTY").rstrip("/")
AZURE_IMAGE_API_KEY = os.environ.get("AZURE_IMAGE_API_KEY", "EMPTY")


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
    notify: AgentUpdateEvent,
):

    await notify(
        id="image_generation",
        status="run in_progress",
        information="Starting image generation",
    )

    size: str = "1024x1024"
    quality: str = "medium"
    api_version = "2025-04-01-preview"
    deployment_name = "gpt-image-1"
    endpoint = f"{AZURE_IMAGE_ENDPOINT}/openai/deployments/{deployment_name}/images/generations?api-version={api_version}"

    await notify(
        id="image_generation", status="step in_progress", information="Executing Model"
    )

    async with post_request(
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
        if "error" in response:
            print(response["error"])
            await notify(
                id="image_generation",
                status="step failed",
                information=response["error"],
            )
            return []

        await notify(
            id="image_generation",
            status="step in_progress",
            information="fetching images" if n > 1 else "fetching image",
        )

        # save the image to a file
        # iterate through the images and save them
        if not response["data"]:
            print("No images found in the response.")
            return []

        await notify(
            id="image_generation",
            status="step in_progress",
            information="storing images" if n > 1 else "storing image",
        )

        base64_images = [
            item["b64_json"] for item in response["data"] if item["b64_json"]
        ]

        async for blob_name in save_image_blobs(base64_images):
            await notify(
                id="image_generation",
                status="step completed",
                content=Content(
                    type="image",
                    content=[
                        {
                            "type": "image",
                            "description": description,
                            "size": size,
                            "quality": quality,
                            "image_url": blob_name,
                        }
                    ],
                ),
                output=True,
            )

        await notify(
            id="image_generation",
            status="run completed",
            information="Image generation complete",
        )


@agent(
    name="Image Editing Agent",
    description="This Agent can generate a number of images based upon a detailed description AND a starting image to edit. This agent is based on the GPT-Image-1 model and is capable of editing generated images in a variety of styles. It can also edit images in a specific style, such as a painting or a photograph. The agent can also generate images with different levels of detail and complexity.",
)
async def gpt_image_edit(
    description: Annotated[
        str,
        "The detailed description of the image to be generated. The more detailed the description, the better the image will be. Make sure to include the style of the image, the colors, and any other details that will help the model generate a better image.",
    ],
    image: Annotated[
        str,
        "The base64 encoded image to be used as a starting point for the generation. This image will be used as a reference for the model to generate the new image.",
    ],
    n: Annotated[int, "number of images to generate"],
    notify: AgentUpdateEvent,
):
    pass


@agent(
    name="Sora Video Generation Agent",
    description="This agent can generate a number of videos based upon a detailed description. This agent is based on the Sora model and is capable of generating videos in a variety of styles. It can also generate videos in a specific style, such as a painting or a photograph. The agent can also generate videos with different levels of detail and complexity.",
)
async def sora_video_generation(
    description: Annotated[
        str,
        "The detailed description of the video to be generated. The more detailed the description, the better the video will be. Make sure to include the style of the video, the colors, and any other details that will help the model generate a better video.",
    ],
    n: Annotated[int, "number of videos to generate"],
    notify: AgentUpdateEvent,
):
    pass


@agent(
    name="BuildEvents - Post to LinkedIn Agent - Local",
    description="""
You are a publishing agent responsible for posting finalized and approved LinkedIn posts. 

You will receive as input:
- title (string): Title of the post.
- content (string): Body of the post or finalized draft.
- image_url (string, optional): Format should always start with https://sustineo-api.jollysmoke-a2364653.eastus2.azurecontainerapps.io/images/
- example image_url: https://sustineo-api.jollysmoke-a2364653.eastus2.azurecontainerapps.io/images/acd7fe97-8d22-48ca-a06c-d38b769a8924.png
- use the provided image_url

You will take the draft and publish the post on Linkedln by calling the OpenAPI tool.""",
)
async def publish_linkedin_post(
    content: Annotated[str, "Body of the post or finalized draft in markdown."],
    image_url: Annotated[
        str,
        "Format should always start with https://sustineo-api.jollysmoke-a2364653.eastus2.azurecontainerapps.io/images/",
    ],
    notify: AgentUpdateEvent,
):
    instructions = f"""
Use the following `image_url`: {image_url}
Use this `image_url` exactly as it is. Do not change the image_url or the content of the post.
The post should be in markdown format.
"""
    await execute_foundry_agent(
        agent_id="asst_MbvKNQxeTr5DL1wuE8DRYR3M",
        additional_instructions=instructions,
        query=f"Can you write a LinkedIn post based on the following content?\n\n{content}",
        tools={},
        notify=notify,
    )
