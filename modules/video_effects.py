"""Video effects module using MoviePy."""

import logging
from pathlib import Path
from typing import List, Optional, Callable
import numpy as np
from moviepy.editor import (
    ImageClip,
    CompositeVideoClip,
    concatenate_videoclips,
)
from moviepy.video.fx.all import resize, fadein, fadeout
from config import settings

logger = logging.getLogger(__name__)


def zoom_in_effect(get_frame, t):
    """Create a zoom-in effect on a frame.

    Args:
        get_frame: Frame getter function
        t: Time in seconds

    Returns:
        Transformed frame
    """
    frame = get_frame(t)
    h, w = frame.shape[:2]

    # Calculate zoom factor (zoom from 1.0 to 1.3 over the duration)
    zoom = 1.0 + 0.3 * t / 3.0  # Adjust based on clip duration

    # Calculate new dimensions
    new_h, new_w = int(h * zoom), int(w * zoom)

    # Resize frame
    from PIL import Image

    img = Image.fromarray(frame)
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop to original size
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    img_cropped = img_resized.crop((left, top, left + w, top + h))

    return np.array(img_cropped)


def zoom_out_effect(get_frame, t):
    """Create a zoom-out effect on a frame.

    Args:
        get_frame: Frame getter function
        t: Time in seconds

    Returns:
        Transformed frame
    """
    frame = get_frame(t)
    h, w = frame.shape[:2]

    # Calculate zoom factor (zoom from 1.3 to 1.0 over the duration)
    zoom = 1.3 - 0.3 * t / 3.0

    # Calculate new dimensions
    new_h, new_w = int(h * zoom), int(w * zoom)

    # Resize and pad
    from PIL import Image

    img = Image.fromarray(frame)

    if zoom < 1.0:
        # If zoomed out, resize and center on black background
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        background = Image.new("RGB", (w, h), (0, 0, 0))
        left = (w - new_w) // 2
        top = (h - new_h) // 2
        background.paste(img_resized, (left, top))
        return np.array(background)
    else:
        # If zoomed in, crop to center
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        img_cropped = img_resized.crop((left, top, left + w, top + h))
        return np.array(img_cropped)


def pan_effect(get_frame, t, direction="right"):
    """Create a panning effect on a frame.

    Args:
        get_frame: Frame getter function
        t: Time in seconds
        direction: Pan direction ('left', 'right', 'up', 'down')

    Returns:
        Transformed frame
    """
    frame = get_frame(t)
    h, w = frame.shape[:2]

    # Enlarge frame
    zoom = 1.2
    new_h, new_w = int(h * zoom), int(w * zoom)

    from PIL import Image

    img = Image.fromarray(frame)
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)

    # Calculate pan offset (0 to max over duration)
    progress = t / 3.0  # Assume 3 second clips

    if direction == "right":
        left = int((new_w - w) * progress)
        top = (new_h - h) // 2
    elif direction == "left":
        left = int((new_w - w) * (1 - progress))
        top = (new_h - h) // 2
    elif direction == "down":
        left = (new_w - w) // 2
        top = int((new_h - h) * progress)
    else:  # up
        left = (new_w - w) // 2
        top = int((new_h - h) * (1 - progress))

    img_cropped = img_resized.crop((left, top, left + w, top + h))
    return np.array(img_cropped)


def create_video_clip(
    image_path: Path,
    duration: float,
    effect: str = "zoom_in",
    fps: int = 24,
) -> ImageClip:
    """Create a video clip from an image with effects.

    Args:
        image_path: Path to the image file
        duration: Duration of the clip in seconds
        effect: Effect to apply ('zoom_in', 'zoom_out', 'pan_right', 'pan_left', 'none')
        fps: Frames per second

    Returns:
        ImageClip with applied effects
    """
    logger.debug(f"Creating clip from {image_path.name} with {effect} effect")

    # Create base clip
    clip = ImageClip(str(image_path), duration=duration)

    # Apply effect
    if effect == "zoom_in":
        clip = clip.fl(zoom_in_effect)
    elif effect == "zoom_out":
        clip = clip.fl(zoom_out_effect)
    elif effect == "pan_right":
        clip = clip.fl(lambda gf, t: pan_effect(gf, t, "right"))
    elif effect == "pan_left":
        clip = clip.fl(lambda gf, t: pan_effect(gf, t, "left"))
    elif effect == "pan_up":
        clip = clip.fl(lambda gf, t: pan_effect(gf, t, "up"))
    elif effect == "pan_down":
        clip = clip.fl(lambda gf, t: pan_effect(gf, t, "down"))

    # Add fade in/out
    clip = fadein(clip, 0.5)
    clip = fadeout(clip, 0.5)

    clip = clip.set_fps(fps)

    return clip


def create_video_clips(
    image_paths: List[Path],
    scenes: List,
    output_dir: Path,
    effects: Optional[List[str]] = None,
) -> List[Path]:
    """Create video clips from images with effects.

    Args:
        image_paths: List of image file paths
        scenes: List of Scene objects with duration info
        output_dir: Directory to save video clips
        effects: List of effects to cycle through. If None, uses default variety

    Returns:
        List of paths to generated video clips

    Raises:
        RuntimeError: If video creation fails
    """
    logger.info(f"Creating {len(image_paths)} video clips with MoviePy...")

    if effects is None:
        # Cycle through various effects for visual variety
        effects = ["zoom_in", "zoom_out", "pan_right", "pan_left"]

    output_dir.mkdir(parents=True, exist_ok=True)
    clip_paths = []

    for i, (image_path, scene) in enumerate(zip(image_paths, scenes)):
        try:
            # Select effect (cycle through available effects)
            effect = effects[i % len(effects)]

            # Create clip
            clip = create_video_clip(
                image_path,
                duration=scene.duration,
                effect=effect,
                fps=settings.video_fps,
            )

            # Save clip
            output_path = output_dir / f"clip_{scene.scene_number:03d}.mp4"
            clip.write_videofile(
                str(output_path),
                fps=settings.video_fps,
                codec="libx264",
                audio=False,
                verbose=False,
                logger=None,
            )

            clip.close()
            clip_paths.append(output_path)

            logger.debug(f"Created clip: {output_path.name} with {effect} effect")

        except Exception as e:
            logger.error(f"Failed to create clip for scene {scene.scene_number}: {e}")
            raise RuntimeError(f"Video clip creation failed: {e}")

    logger.info(f"Successfully created {len(clip_paths)} video clips")
    return clip_paths


def concatenate_clips(clip_paths: List[Path], output_path: Path):
    """Concatenate video clips into a single video.

    Args:
        clip_paths: List of video clip paths
        output_path: Output file path

    Raises:
        RuntimeError: If concatenation fails
    """
    logger.info(f"Concatenating {len(clip_paths)} clips...")

    try:
        from moviepy.editor import VideoFileClip

        # Load all clips
        clips = [VideoFileClip(str(path)) for path in clip_paths]

        # Concatenate
        final_clip = concatenate_videoclips(clips, method="compose")

        # Write output
        final_clip.write_videofile(
            str(output_path),
            fps=settings.video_fps,
            codec="libx264",
            audio=False,
            verbose=False,
            logger=None,
        )

        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()

        logger.info(f"Concatenated video saved to: {output_path}")

    except Exception as e:
        logger.error(f"Failed to concatenate clips: {e}")
        raise RuntimeError(f"Video concatenation failed: {e}")
