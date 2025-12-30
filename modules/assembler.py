"""Video assembly module using FFmpeg."""

import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def check_ffmpeg():
    """Check if FFmpeg is installed.

    Raises:
        RuntimeError: If FFmpeg is not found
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError(
            "FFmpeg not found. Please install FFmpeg: https://ffmpeg.org/download.html"
        )


def add_audio_to_video(
    video_path: Path, audio_path: Path, output_path: Path
) -> Path:
    """Add audio track to video using FFmpeg.

    Args:
        video_path: Path to the video file (no audio)
        audio_path: Path to the audio file
        output_path: Path for the output video

    Returns:
        Path to the output video

    Raises:
        RuntimeError: If FFmpeg command fails
    """
    logger.info(f"Adding audio to video...")

    check_ffmpeg()

    try:
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-c:v",
            "copy",  # Copy video codec
            "-c:a",
            "aac",  # Encode audio to AAC
            "-strict",
            "experimental",
            "-shortest",  # Match shortest stream
            "-y",  # Overwrite output
            str(output_path),
        ]

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )

        logger.info(f"Video with audio saved to: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr.decode()}")
        raise RuntimeError(f"Failed to add audio to video: {e}")


def burn_subtitles(
    video_path: Path,
    subtitle_path: Path,
    output_path: Path,
    subtitle_style: Optional[str] = None,
) -> Path:
    """Burn subtitles into video using FFmpeg.

    Args:
        video_path: Path to the video file
        subtitle_path: Path to the .srt subtitle file
        output_path: Path for the output video
        subtitle_style: Optional ASS subtitle style string

    Returns:
        Path to the output video

    Raises:
        RuntimeError: If FFmpeg command fails
    """
    logger.info(f"Burning subtitles into video...")

    check_ffmpeg()

    try:
        # Default subtitle style if not provided
        if subtitle_style is None:
            # ASS subtitle style format
            # FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1
            subtitle_style = (
                "FontName=Arial,FontSize=24,PrimaryColour=&HFFFFFF,"
                "OutlineColour=&H000000,BorderStyle=3,Outline=2,Shadow=0,"
                "MarginV=20,Bold=1"
            )

        # FFmpeg command to burn subtitles
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vf",
            f"subtitles={subtitle_path}:force_style='{subtitle_style}'",
            "-c:a",
            "copy",  # Copy audio codec
            "-y",  # Overwrite output
            str(output_path),
        ]

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )

        logger.info(f"Video with subtitles saved to: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr.decode()}")
        raise RuntimeError(f"Failed to burn subtitles: {e}")


def assemble_final_video(
    video_path: Path,
    audio_path: Path,
    subtitle_path: Path,
    output_path: Path,
    subtitle_style: Optional[str] = None,
) -> Path:
    """Assemble final video with audio and subtitles.

    This is the main assembly function that combines:
    1. Video clips (already concatenated)
    2. Audio voiceover
    3. Burned-in subtitles

    Args:
        video_path: Path to the concatenated video file
        audio_path: Path to the audio file
        subtitle_path: Path to the .srt subtitle file
        output_path: Path for the final output video
        subtitle_style: Optional ASS subtitle style string

    Returns:
        Path to the final video

    Raises:
        RuntimeError: If assembly fails
    """
    logger.info("Assembling final video with audio and subtitles...")

    check_ffmpeg()

    try:
        # Default subtitle style if not provided
        if subtitle_style is None:
            subtitle_style = (
                "FontName=Arial,FontSize=24,PrimaryColour=&HFFFFFF,"
                "OutlineColour=&H000000,BorderStyle=3,Outline=2,Shadow=0,"
                "MarginV=20,Bold=1"
            )

        # Single FFmpeg command to add audio and burn subtitles
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-vf",
            f"subtitles={subtitle_path}:force_style='{subtitle_style}'",
            "-c:a",
            "aac",
            "-strict",
            "experimental",
            "-shortest",  # Match shortest stream
            "-y",  # Overwrite output
            str(output_path),
        ]

        logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )

        logger.info(f"Final video saved to: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr.decode()}")
        raise RuntimeError(f"Failed to assemble final video: {e}")


def extract_audio_from_video(video_path: Path, output_path: Path) -> Path:
    """Extract audio from video file.

    Args:
        video_path: Path to the video file
        output_path: Path for the extracted audio file

    Returns:
        Path to the extracted audio

    Raises:
        RuntimeError: If extraction fails
    """
    logger.info(f"Extracting audio from {video_path}...")

    check_ffmpeg()

    try:
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vn",  # No video
            "-acodec",
            "mp3",  # MP3 codec
            "-y",  # Overwrite
            str(output_path),
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        logger.info(f"Audio extracted to: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr.decode()}")
        raise RuntimeError(f"Failed to extract audio: {e}")


def convert_audio_format(
    input_path: Path, output_path: Path, format: str = "mp3"
) -> Path:
    """Convert audio to different format.

    Args:
        input_path: Path to input audio file
        output_path: Path for output audio file
        format: Target format (mp3, wav, aac)

    Returns:
        Path to converted audio

    Raises:
        RuntimeError: If conversion fails
    """
    logger.info(f"Converting audio to {format}...")

    check_ffmpeg()

    try:
        cmd = [
            "ffmpeg",
            "-i",
            str(input_path),
            "-acodec",
            format if format != "mp3" else "libmp3lame",
            "-y",
            str(output_path),
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        logger.info(f"Audio converted to: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr.decode()}")
        raise RuntimeError(f"Failed to convert audio: {e}")
