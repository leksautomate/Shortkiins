"""Scene division module using Groq API."""

import json
import logging
from typing import List, Dict, Optional
from groq import Groq
from config import settings

logger = logging.getLogger(__name__)


class Scene:
    """Represents a single scene in the video."""

    def __init__(
        self,
        scene_number: int,
        text: str,
        image_prompt: str,
        duration: float = 3.0,
        start_time: float = 0.0,
    ):
        """Initialize a scene.

        Args:
            scene_number: Scene index
            text: Narration text for this scene
            image_prompt: Detailed prompt for image generation
            duration: Duration in seconds
            start_time: Start time in the video
        """
        self.scene_number = scene_number
        self.text = text
        self.image_prompt = image_prompt
        self.duration = duration
        self.start_time = start_time

    def to_dict(self) -> Dict:
        """Convert scene to dictionary."""
        return {
            "scene_number": self.scene_number,
            "text": self.text,
            "image_prompt": self.image_prompt,
            "duration": self.duration,
            "start_time": self.start_time,
        }

    def __repr__(self):
        return f"Scene({self.scene_number}: {self.text[:30]}...)"


def divide_into_scenes(
    script: str,
    scene_duration: float = 3.0,
    model: str = "llama-3.3-70b-versatile",
) -> List[Scene]:
    """Divide script into scenes with image prompts using Groq API.

    Args:
        script: The full script text
        scene_duration: Target duration for each scene in seconds
        model: Groq model to use

    Returns:
        List of Scene objects

    Raises:
        RuntimeError: If scene division fails
    """
    logger.info("Dividing script into scenes with Groq API...")

    if not settings.groq_api_key:
        raise ValueError("Groq API key not configured")

    try:
        client = Groq(api_key=settings.groq_api_key)

        # Create prompt for scene division
        system_prompt = """You are a video production assistant. Your task is to divide a script into scenes, where each scene lasts approximately {duration} seconds when narrated.

For each scene, provide:
1. The narration text (what will be spoken)
2. A detailed image prompt for generating background visuals

Return the result as a JSON array with this structure:
[
  {
    "text": "Scene narration text",
    "image_prompt": "Detailed visual description for image generation"
  }
]

Guidelines:
- Each scene should be a complete thought or sentence
- Image prompts should be detailed, cinematic, and visually compelling
- Include style descriptors (e.g., "cinematic lighting", "vibrant colors", "wide angle")
- Consider visual continuity between scenes
- Make prompts specific enough for AI image generation""".format(
            duration=scene_duration
        )

        user_prompt = f"""Divide this script into scenes of approximately {scene_duration} seconds each:

{script}

Return only the JSON array, no additional text."""

        # Call Groq API
        logger.info(f"Calling Groq API with model: {model}")
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )

        # Parse response
        response_text = completion.choices[0].message.content
        logger.debug(f"Groq response: {response_text}")

        # Parse JSON response
        try:
            # Handle both direct array and wrapped object
            data = json.loads(response_text)
            if isinstance(data, dict):
                # If wrapped in an object, look for common keys
                scenes_data = (
                    data.get("scenes")
                    or data.get("data")
                    or data.get("result")
                    or list(data.values())[0]
                )
            else:
                scenes_data = data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise RuntimeError(f"Invalid JSON response from Groq: {e}")

        # Create Scene objects
        scenes = []
        current_time = 0.0

        for i, scene_data in enumerate(scenes_data):
            scene = Scene(
                scene_number=i + 1,
                text=scene_data["text"],
                image_prompt=scene_data["image_prompt"],
                duration=scene_duration,
                start_time=current_time,
            )
            scenes.append(scene)
            current_time += scene_duration

        logger.info(f"Created {len(scenes)} scenes")
        for scene in scenes:
            logger.debug(f"  {scene}")

        return scenes

    except Exception as e:
        logger.error(f"Failed to divide script into scenes: {e}")
        raise RuntimeError(f"Scene division failed: {e}")


def save_scenes_to_json(scenes: List[Scene], output_path: str):
    """Save scenes to a JSON file.

    Args:
        scenes: List of Scene objects
        output_path: Path to save JSON file
    """
    data = [scene.to_dict() for scene in scenes]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Scenes saved to: {output_path}")


def load_scenes_from_json(input_path: str) -> List[Scene]:
    """Load scenes from a JSON file.

    Args:
        input_path: Path to JSON file

    Returns:
        List of Scene objects
    """
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenes = [
        Scene(
            scene_number=scene_data["scene_number"],
            text=scene_data["text"],
            image_prompt=scene_data["image_prompt"],
            duration=scene_data["duration"],
            start_time=scene_data["start_time"],
        )
        for scene_data in data
    ]

    logger.info(f"Loaded {len(scenes)} scenes from {input_path}")
    return scenes
