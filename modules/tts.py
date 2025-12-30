"""Text-to-speech module using Inworld AI API."""

import logging
from pathlib import Path
from typing import Optional
import requests
from config import settings

logger = logging.getLogger(__name__)


class InworldTTS:
    """Inworld AI Text-to-Speech client."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Inworld TTS client.

        Args:
            api_key: Inworld API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.inworld_api_key
        self.workspace = settings.inworld_workspace
        self.scene = settings.inworld_scene
        self.base_url = "https://api.inworld.ai"

        if not self.api_key:
            raise ValueError("Inworld API key not configured")

    def generate_audio(
        self,
        text: str,
        output_path: Path,
        voice_id: Optional[str] = None,
        audio_format: str = "mp3",
    ) -> Path:
        """Generate audio from text using Inworld AI.

        Args:
            text: The text to convert to speech
            output_path: Where to save the generated audio
            voice_id: Optional custom voice ID
            audio_format: Audio format (mp3, wav)

        Returns:
            Path to the generated audio file

        Raises:
            RuntimeError: If audio generation fails
        """
        logger.info(f"Generating voiceover with Inworld AI...")

        try:
            # Inworld AI API endpoint for TTS
            # Note: This is a simplified example. Actual implementation
            # would use the Inworld SDK and proper authentication
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "text": text,
                "workspace": self.workspace,
                "scene": self.scene,
                "voice_id": voice_id,
                "audio_format": audio_format,
            }

            # For actual implementation, use the Inworld SDK
            # from inworld.client import InworldClient
            # client = InworldClient(api_key=self.api_key)
            # audio_data = client.generate_speech(text, voice_id)

            # Placeholder for actual API call
            logger.warning(
                "Using placeholder TTS. Implement actual Inworld API integration."
            )

            # For now, create a dummy file to demonstrate the pipeline
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.touch()

            logger.info(f"Audio saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")
            raise RuntimeError(f"TTS generation failed: {e}")


def generate_voiceover(
    script: str,
    output_path: Path,
    voice_id: Optional[str] = None,
) -> Path:
    """Generate voiceover from script using Inworld AI.

    Args:
        script: The script text
        output_path: Where to save the audio file
        voice_id: Optional custom voice ID

    Returns:
        Path to the generated audio file
    """
    tts = InworldTTS()
    return tts.generate_audio(script, output_path, voice_id)


# Alternative: OpenAI TTS as a fallback option
def generate_voiceover_openai(script: str, output_path: Path) -> Path:
    """Alternative TTS using OpenAI (requires openai package).

    Args:
        script: The script text
        output_path: Where to save the audio file

    Returns:
        Path to the generated audio file
    """
    try:
        from openai import OpenAI

        client = OpenAI()
        response = client.audio.speech.create(
            model="tts-1-hd", voice="alloy", input=script
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        response.stream_to_file(output_path)

        logger.info(f"Audio saved to: {output_path}")
        return output_path

    except ImportError:
        raise RuntimeError("OpenAI package not installed. Run: pip install openai")
    except Exception as e:
        raise RuntimeError(f"OpenAI TTS failed: {e}")
