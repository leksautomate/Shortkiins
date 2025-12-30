"""Subtitle generation module using OpenAI Whisper."""

import logging
from pathlib import Path
from typing import Optional
import whisper
from datetime import timedelta

logger = logging.getLogger(__name__)


def format_timestamp(seconds: float) -> str:
    """Format seconds to SRT timestamp format (HH:MM:SS,mmm).

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string
    """
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    millis = int((td.total_seconds() % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def create_srt_content(segments: list) -> str:
    """Create SRT file content from Whisper segments.

    Args:
        segments: List of transcription segments from Whisper

    Returns:
        SRT formatted string
    """
    srt_content = []

    for i, segment in enumerate(segments, start=1):
        start_time = format_timestamp(segment["start"])
        end_time = format_timestamp(segment["end"])
        text = segment["text"].strip()

        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(text)
        srt_content.append("")  # Empty line between subtitles

    return "\n".join(srt_content)


def generate_subtitles(
    audio_path: Path,
    output_path: Path,
    model_name: str = "base",
    language: Optional[str] = None,
) -> Path:
    """Generate SRT subtitles from audio file using Whisper.

    Args:
        audio_path: Path to the audio file (.mp3, .wav, etc.)
        output_path: Path where to save the .srt file
        model_name: Whisper model to use (tiny, base, small, medium, large)
        language: Optional language code (e.g., 'en', 'es')

    Returns:
        Path to the generated SRT file

    Raises:
        RuntimeError: If subtitle generation fails
    """
    logger.info(f"Generating subtitles from {audio_path}...")
    logger.info(f"Loading Whisper model: {model_name}")

    try:
        # Load Whisper model
        model = whisper.load_model(model_name)

        # Transcribe audio
        logger.info("Transcribing audio...")
        result = model.transcribe(
            str(audio_path),
            language=language,
            task="transcribe",
            verbose=False,
        )

        # Create SRT content
        srt_content = create_srt_content(result["segments"])

        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(srt_content, encoding="utf-8")

        logger.info(f"Subtitles saved to: {output_path}")
        logger.info(f"Detected language: {result.get('language', 'unknown')}")

        return output_path

    except Exception as e:
        logger.error(f"Failed to generate subtitles: {e}")
        raise RuntimeError(f"Subtitle generation failed: {e}")


def generate_subtitles_with_word_timestamps(
    audio_path: Path,
    output_path: Path,
    model_name: str = "base",
) -> Path:
    """Generate subtitles with word-level timestamps for more precise timing.

    Args:
        audio_path: Path to the audio file
        output_path: Path where to save the .srt file
        model_name: Whisper model to use

    Returns:
        Path to the generated SRT file
    """
    logger.info(f"Generating word-level subtitles from {audio_path}...")

    try:
        model = whisper.load_model(model_name)

        result = model.transcribe(
            str(audio_path), word_timestamps=True, verbose=False
        )

        # Create more granular subtitles
        segments = []
        for segment in result["segments"]:
            if "words" in segment:
                # Group words into chunks (e.g., 5-7 words per subtitle)
                words = segment["words"]
                chunk_size = 6
                for i in range(0, len(words), chunk_size):
                    chunk = words[i : i + chunk_size]
                    if chunk:
                        segments.append(
                            {
                                "start": chunk[0]["start"],
                                "end": chunk[-1]["end"],
                                "text": " ".join(w["word"] for w in chunk),
                            }
                        )
            else:
                segments.append(segment)

        srt_content = create_srt_content(segments)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(srt_content, encoding="utf-8")

        logger.info(f"Word-level subtitles saved to: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to generate word-level subtitles: {e}")
        raise RuntimeError(f"Word-level subtitle generation failed: {e}")
