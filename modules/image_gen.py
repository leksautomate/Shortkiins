"""Image generation module supporting multiple providers."""

import logging
import time
from pathlib import Path
from typing import Optional, List
import requests
import replicate
from config import settings

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Base class for image generation."""

    def generate(self, prompt: str, output_path: Path) -> Path:
        """Generate an image from a prompt.

        Args:
            prompt: Text description of the image
            output_path: Where to save the generated image

        Returns:
            Path to the generated image
        """
        raise NotImplementedError


class FreepikGenerator(ImageGenerator):
    """Image generator using Freepik Seedream API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Freepik generator.

        Args:
            api_key: Freepik API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.freepik_api_key
        self.base_url = "https://api.freepik.com/v1"

        if not self.api_key:
            raise ValueError("Freepik API key not configured")

    def generate(self, prompt: str, output_path: Path) -> Path:
        """Generate image using Freepik Seedream.

        Args:
            prompt: Image description
            output_path: Output file path

        Returns:
            Path to generated image
        """
        logger.info(f"Generating image with Freepik: {prompt[:50]}...")

        try:
            headers = {
                "X-Freepik-API-Key": self.api_key,
                "Content-Type": "application/json",
            }

            # Freepik Seedream API endpoint
            payload = {
                "prompt": prompt,
                "model": "seedream-4",
                "num_images": 1,
                "style": "cinematic",
                "aspect_ratio": "16:9",
            }

            # Note: This is a placeholder. Actual Freepik API may differ
            response = requests.post(
                f"{self.base_url}/ai/image/generate",
                headers=headers,
                json=payload,
                timeout=60,
            )

            response.raise_for_status()
            data = response.json()

            # Download the generated image
            image_url = data["images"][0]["url"]
            self._download_image(image_url, output_path)

            logger.info(f"Image saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Freepik generation failed: {e}")
            raise RuntimeError(f"Freepik image generation failed: {e}")

    def _download_image(self, url: str, output_path: Path):
        """Download image from URL."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)


class ReplicateGenerator(ImageGenerator):
    """Image generator using Replicate API (supports multiple models)."""

    def __init__(
        self,
        api_token: Optional[str] = None,
        model: str = "stability-ai/sdxl:latest",
    ):
        """Initialize Replicate generator.

        Args:
            api_token: Replicate API token. If not provided, uses settings.
            model: Model identifier (e.g., 'stability-ai/sdxl:latest')
        """
        self.api_token = api_token or settings.replicate_api_token
        self.model = model

        if not self.api_token:
            raise ValueError("Replicate API token not configured")

    def generate(self, prompt: str, output_path: Path) -> Path:
        """Generate image using Replicate.

        Args:
            prompt: Image description
            output_path: Output file path

        Returns:
            Path to generated image
        """
        logger.info(f"Generating image with Replicate ({self.model}): {prompt[:50]}...")

        try:
            # Get dimensions based on aspect ratio
            width, height = settings.get_dimensions()

            # Set API token
            replicate.Client(api_token=self.api_token)

            # Run the model
            output = replicate.run(
                self.model,
                input={
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_outputs": 1,
                },
            )

            # Download the image
            if isinstance(output, list):
                image_url = output[0]
            else:
                image_url = output

            self._download_image(image_url, output_path)

            logger.info(f"Image saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Replicate generation failed: {e}")
            raise RuntimeError(f"Replicate image generation failed: {e}")

    def _download_image(self, url: str, output_path: Path):
        """Download image from URL."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)


class WaveSpeedGenerator(ImageGenerator):
    """Image generator using Wave Speed AI API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Wave Speed generator.

        Args:
            api_key: Wave Speed API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.wavespeed_api_key
        self.base_url = "https://api.wavespeed.ai/api/v3"

        if not self.api_key:
            raise ValueError("Wave Speed API key not configured")

    def generate(self, prompt: str, output_path: Path) -> Path:
        """Generate image using Wave Speed AI.

        Args:
            prompt: Image description
            output_path: Output file path

        Returns:
            Path to generated image
        """
        logger.info(f"Generating image with Wave Speed AI: {prompt[:50]}...")

        try:
            import json

            # Get dimensions based on aspect ratio
            width, height = settings.get_dimensions()

            # Submit generation request
            url = f"{self.base_url}/wavespeed-ai/z-image/turbo"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            payload = {
                "enable_base64_output": False,
                "enable_sync_mode": False,
                "output_format": "jpeg",
                "prompt": prompt,
                "seed": -1,
                "size": f"{width}*{height}",
            }

            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            result = response.json()["data"]
            request_id = result["id"]
            logger.debug(f"Wave Speed task submitted. Request ID: {request_id}")

            # Poll for results
            result_url = f"{self.base_url}/predictions/{request_id}/result"
            headers = {"Authorization": f"Bearer {self.api_key}"}

            max_wait_time = 120  # 2 minutes timeout
            start_time = time.time()

            while True:
                if time.time() - start_time > max_wait_time:
                    raise RuntimeError("Wave Speed generation timed out after 2 minutes")

                response = requests.get(result_url, headers=headers)
                response.raise_for_status()

                result = response.json()["data"]
                status = result["status"]

                if status == "completed":
                    image_url = result["outputs"][0]
                    logger.debug(f"Wave Speed generation completed: {image_url}")
                    self._download_image(image_url, output_path)
                    logger.info(f"Image saved to: {output_path}")
                    return output_path

                elif status == "failed":
                    error = result.get("error", "Unknown error")
                    raise RuntimeError(f"Wave Speed generation failed: {error}")

                else:
                    logger.debug(f"Wave Speed task processing. Status: {status}")
                    time.sleep(0.5)  # Poll every 500ms

        except Exception as e:
            logger.error(f"Wave Speed generation failed: {e}")
            raise RuntimeError(f"Wave Speed image generation failed: {e}")

    def _download_image(self, url: str, output_path: Path):
        """Download image from URL."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)


def generate_images(
    scenes: List,
    output_dir: Path,
    provider: str = "replicate",
    max_retries: int = 3,
) -> List[Path]:
    """Generate images for all scenes.

    Args:
        scenes: List of Scene objects with image_prompt attributes
        output_dir: Directory to save generated images
        provider: Image generation provider ('freepik', 'replicate', 'wavespeed')
        max_retries: Maximum retry attempts for failed generations

    Returns:
        List of paths to generated images

    Raises:
        RuntimeError: If image generation fails
    """
    logger.info(f"Generating {len(scenes)} images using {provider}...")

    # Select generator
    if provider == "freepik":
        generator = FreepikGenerator()
    elif provider == "wavespeed":
        generator = WaveSpeedGenerator()
    else:  # replicate
        generator = ReplicateGenerator()

    output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = []

    for i, scene in enumerate(scenes):
        output_path = output_dir / f"scene_{scene.scene_number:03d}.png"

        # Retry logic
        for attempt in range(max_retries):
            try:
                generator.generate(scene.image_prompt, output_path)
                image_paths.append(output_path)
                break

            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed for scene {scene.scene_number}: {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    raise RuntimeError(
                        f"Failed to generate image for scene {scene.scene_number} after {max_retries} attempts"
                    )

        # Rate limiting
        time.sleep(1)

    logger.info(f"Successfully generated {len(image_paths)} images")
    return image_paths
