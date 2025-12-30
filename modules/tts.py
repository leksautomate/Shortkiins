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


# Alternative: AsyncFlow TTS with word timestamps
class AsyncFlowTTS:
    """AsyncFlow Text-to-Speech with word timestamps."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize AsyncFlow TTS client.

        Args:
            api_key: AsyncFlow API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.asyncflow_api_key
        self.base_url = "https://api.async.ai"  # Replace with actual base URL

        if not self.api_key:
            raise ValueError("AsyncFlow API key not configured")

    def generate_audio(
        self,
        text: str,
        output_path: Path,
        voice_id: str = "e0f39dc4-f691-4e78-bba5-5c636692cc04",
        model_id: str = "asyncflow_v2.0",
        language: Optional[str] = "en",
    ) -> Path:
        """Generate audio with word timestamps using AsyncFlow.

        Args:
            text: The text to convert to speech
            output_path: Where to save the generated audio
            voice_id: Voice ID to use
            model_id: Model to use (asyncflow_v2.0 or asyncflow_multilingual_v1.0)
            language: Language code (ISO 639-1)

        Returns:
            Path to the generated audio file

        Raises:
            RuntimeError: If audio generation fails
        """
        import base64
        import json

        logger.info(f"Generating voiceover with AsyncFlow TTS...")

        try:
            url = f"{self.base_url}/text_to_speech/with_timestamps"
            headers = {
                "x-api-key": self.api_key,
                "version": "v1",
                "Content-Type": "application/json",
            }

            payload = {
                "model_id": model_id,
                "transcript": text,
                "voice": {"mode": "id", "id": voice_id},
                "output_format": {
                    "container": "mp3",
                    "sample_rate": 44100,
                    "bit_rate": 192000,
                },
            }

            if language:
                payload["language"] = language

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()

            # Decode base64 audio
            audio_base64 = result["audio_base64"]
            audio_data = base64.b64decode(audio_base64)

            # Save audio file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(audio_data)

            # Save word timestamps for reference
            alignment = result.get("alignment")
            if alignment:
                timestamps_path = output_path.with_suffix(".timestamps.json")
                with open(timestamps_path, "w") as f:
                    json.dump(alignment, f, indent=2)
                logger.info(f"Word timestamps saved to: {timestamps_path}")

            logger.info(f"Audio saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")
            raise RuntimeError(f"AsyncFlow TTS generation failed: {e}")


def generate_voiceover_asyncflow(
    script: str,
    output_path: Path,
    voice_id: Optional[str] = None,
) -> Path:
    """Generate voiceover using AsyncFlow TTS with word timestamps.

    Args:
        script: The script text
        output_path: Where to save the audio file
        voice_id: Optional custom voice ID

    Returns:
        Path to the generated audio file
    """
    tts = AsyncFlowTTS()
    default_voice = "e0f39dc4-f691-4e78-bba5-5c636692cc04"
    return tts.generate_audio(script, output_path, voice_id or default_voice)
