"""Configuration management for the video generator pipeline."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    inworld_api_key: str = Field(default="", alias="INWORLD_API_KEY")
    inworld_workspace: str = Field(default="", alias="INWORLD_WORKSPACE")
    inworld_scene: str = Field(default="", alias="INWORLD_SCENE")
    asyncflow_api_key: str = Field(default="", alias="ASYNCFLOW_API_KEY")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    freepik_api_key: str = Field(default="", alias="FREEPIK_API_KEY")
    replicate_api_token: str = Field(default="", alias="REPLICATE_API_TOKEN")
    wavespeed_api_key: str = Field(default="", alias="WAVESPEED_API_KEY")

    # Directories
    output_dir: Path = Field(default=Path("output"), alias="OUTPUT_DIR")
    temp_dir: Path = Field(default=Path("temp"), alias="TEMP_DIR")

    # Video Settings
    scene_duration: int = Field(default=3, alias="SCENE_DURATION")
    video_fps: int = Field(default=24, alias="VIDEO_FPS")
    aspect_ratio: str = Field(default="16:9", alias="ASPECT_RATIO")  # "16:9" or "9:16"
    video_width: int = Field(default=1280, alias="VIDEO_WIDTH")
    video_height: int = Field(default=720, alias="VIDEO_HEIGHT")

    def get_dimensions(self) -> tuple[int, int]:
        """Get video dimensions based on aspect ratio.

        Returns:
            Tuple of (width, height)
        """
        if self.aspect_ratio == "9:16":
            return (720, 1280)  # Portrait (TikTok, Reels, Shorts)
        else:  # 16:9
            return (1280, 720)  # Landscape (YouTube, standard)

    # Whisper Settings
    whisper_model: str = Field(default="base", alias="WHISPER_MODEL")

    # Image Generation
    image_model: str = Field(default="seedream4", alias="IMAGE_MODEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def ensure_directories(self):
        """Create output and temp directories if they don't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
