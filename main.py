#!/usr/bin/env python3
"""Main video generator pipeline orchestrator."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from config import settings
from modules import (
    generate_voiceover,
    generate_subtitles,
    divide_into_scenes,
    generate_images,
    create_video_clips,
    assemble_final_video,
)
from modules.video_effects import concatenate_clips
from modules.scene_division import save_scenes_to_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class VideoPipeline:
    """Main video generation pipeline."""

    def __init__(
        self,
        script: str,
        output_path: Path,
        scene_duration: float = 3.0,
        image_provider: str = "replicate",
        voice_id: Optional[str] = None,
    ):
        """Initialize the video pipeline.

        Args:
            script: The script text to convert to video
            output_path: Path for the final output video
            scene_duration: Duration of each scene in seconds
            image_provider: Image generation provider
            voice_id: Optional custom voice ID for TTS
        """
        self.script = script
        self.output_path = Path(output_path)
        self.scene_duration = scene_duration
        self.image_provider = image_provider
        self.voice_id = voice_id

        # Ensure directories exist
        settings.ensure_directories()

        # Setup temp directory for this run
        self.temp_dir = settings.temp_dir / self.output_path.stem
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """Run the complete video generation pipeline."""
        logger.info("=" * 60)
        logger.info("Starting Video Generation Pipeline")
        logger.info("=" * 60)

        try:
            # Step 1: Generate voiceover
            logger.info("\n[Step 1/7] Generating voiceover...")
            audio_path = self.temp_dir / "voiceover.mp3"
            generate_voiceover(self.script, audio_path, self.voice_id)

            # Step 2: Generate subtitles
            logger.info("\n[Step 2/7] Generating subtitles...")
            subtitle_path = self.temp_dir / "subtitles.srt"
            generate_subtitles(audio_path, subtitle_path)

            # Step 3: Divide script into scenes
            logger.info("\n[Step 3/7] Dividing script into scenes...")
            scenes = divide_into_scenes(self.script, self.scene_duration)

            # Save scenes for reference
            scenes_json = self.temp_dir / "scenes.json"
            save_scenes_to_json(scenes, scenes_json)
            logger.info(f"Scene breakdown saved to: {scenes_json}")

            # Step 4: Generate images for each scene
            logger.info("\n[Step 4/7] Generating images...")
            image_dir = self.temp_dir / "images"
            image_paths = generate_images(
                scenes, image_dir, provider=self.image_provider
            )

            # Step 5: Create video clips from images
            logger.info("\n[Step 5/7] Creating video clips with effects...")
            clips_dir = self.temp_dir / "clips"
            clip_paths = create_video_clips(image_paths, scenes, clips_dir)

            # Step 6: Concatenate video clips
            logger.info("\n[Step 6/7] Concatenating video clips...")
            concatenated_video = self.temp_dir / "concatenated.mp4"
            concatenate_clips(clip_paths, concatenated_video)

            # Step 7: Assemble final video
            logger.info("\n[Step 7/7] Assembling final video...")
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            assemble_final_video(
                concatenated_video,
                audio_path,
                subtitle_path,
                self.output_path,
            )

            logger.info("\n" + "=" * 60)
            logger.info("Video Generation Complete!")
            logger.info(f"Output: {self.output_path}")
            logger.info(f"Temp files: {self.temp_dir}")
            logger.info("=" * 60)

            return self.output_path

        except Exception as e:
            logger.error(f"\nPipeline failed: {e}", exc_info=True)
            raise


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Automated Video Generator Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate video from text
  python main.py --script "Your script here" --output output/video.mp4

  # Generate from file
  python main.py --script-file input.txt --output output/video.mp4

  # Customize settings
  python main.py --script-file input.txt \\
                 --output output/video.mp4 \\
                 --scene-duration 5 \\
                 --image-provider wavespeed \\
                 --voice-id custom_voice_123
        """,
    )

    # Script input
    script_group = parser.add_mutually_exclusive_group(required=True)
    script_group.add_argument("--script", type=str, help="Script text directly")
    script_group.add_argument(
        "--script-file", type=Path, help="Path to script text file"
    )

    # Output
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/video.mp4"),
        help="Output video path (default: output/video.mp4)",
    )

    # Optional parameters
    parser.add_argument(
        "--scene-duration",
        type=float,
        default=3.0,
        help="Duration of each scene in seconds (default: 3.0)",
    )

    parser.add_argument(
        "--image-provider",
        choices=["freepik", "replicate", "wavespeed"],
        default="replicate",
        help="Image generation provider (default: replicate)",
    )

    parser.add_argument(
        "--voice-id",
        type=str,
        help="Custom voice ID for TTS (optional)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load script
    if args.script:
        script = args.script
    else:
        script = args.script_file.read_text(encoding="utf-8")
        logger.info(f"Loaded script from: {args.script_file}")

    # Validate script
    if not script.strip():
        logger.error("Script is empty!")
        sys.exit(1)

    logger.info(f"Script length: {len(script)} characters")

    # Run pipeline
    try:
        pipeline = VideoPipeline(
            script=script,
            output_path=args.output,
            scene_duration=args.scene_duration,
            image_provider=args.image_provider,
            voice_id=args.voice_id,
        )

        output_path = pipeline.run()

        print(f"\n✅ Success! Video generated: {output_path}")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
