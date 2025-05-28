"""
Simplified unit tests for agent functions with proper async mocking.
"""
import pytest
from unittest.mock import AsyncMock, patch
import base64

from api.agent.agents import gpt_image_generation, publish_linkedin_post
from api.model import Content


class TestAgentFunctions:
    """Simplified test cases for agent functions."""

    @pytest.fixture
    def mock_notify(self):
        """Create a mock notify function."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_gpt_image_generation_basic(self, mock_notify):
        """Test basic image generation functionality."""
        description = "A beautiful sunset"
        n = 1
        
        # Mock response
        mock_response = {
            "data": [{"b64_json": base64.b64encode(b"fake_image").decode()}]
        }

        with patch("api.agent.agents.post_request") as mock_post, \
             patch("api.agent.agents.save_image_blobs") as mock_save_blobs, \
             patch("api.agent.agents.AZURE_IMAGE_ENDPOINT", "https://test.endpoint.com"), \
             patch("api.agent.agents.AZURE_IMAGE_API_KEY", "test_key"):

            # Set up mock context manager for post_request
            mock_post.return_value.__aenter__.return_value = mock_response

            # Set up mock generator for save_image_blobs
            async def mock_blob_generator(images):
                yield "test_blob.png"
            mock_save_blobs.return_value = mock_blob_generator([])

            await gpt_image_generation(description, n, mock_notify)

            # Verify post_request was called
            mock_post.assert_called_once()
            
            # Verify notify was called multiple times
            assert mock_notify.call_count >= 4  # At least start, execute, fetch, complete

    @pytest.mark.asyncio
    async def test_gpt_image_generation_error_handling(self, mock_notify):
        """Test error handling in image generation."""
        description = "Test"
        n = 1
        
        # Mock error response
        mock_response = {"error": "API Error"}

        with patch("api.agent.agents.post_request") as mock_post, \
             patch("api.agent.agents.AZURE_IMAGE_ENDPOINT", "https://test.endpoint.com"), \
             patch("api.agent.agents.AZURE_IMAGE_API_KEY", "test_key"):

            mock_post.return_value.__aenter__.return_value = mock_response

            result = await gpt_image_generation(description, n, mock_notify)
            
            # Should return empty list on error
            assert result == []

    @pytest.mark.asyncio
    async def test_publish_linkedin_post(self, mock_notify):
        """Test LinkedIn post publishing."""
        content = "Test post content"
        image_url = "https://sustineo-api.jollysmoke-a2364653.eastus2.azurecontainerapps.io/images/test.png"

        with patch("api.agent.agents.execute_foundry_agent") as mock_execute:
            await publish_linkedin_post(content, image_url, mock_notify)

            # Verify execute_foundry_agent was called with correct parameters
            mock_execute.assert_called_once()
            call_kwargs = mock_execute.call_args[1]
            
            assert call_kwargs["agent_id"] == "asst_MbvKNQxeTr5DL1wuE8DRYR3M"
            assert image_url in call_kwargs["additional_instructions"]
            assert content in call_kwargs["query"]
            assert call_kwargs["notify"] == mock_notify

    @pytest.mark.asyncio
    async def test_content_creation(self):
        """Test Content model creation."""
        content = Content(
            type="image",
            content=[
                {
                    "type": "image",
                    "description": "Test image",
                    "url": "test.png"
                }
            ]
        )
        
        assert content.type == "image"
        assert len(content.content) == 1
        assert content.content[0]["description"] == "Test image"


if __name__ == "__main__":
    pytest.main([__file__])
