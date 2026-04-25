"""Video compiler — stitches slide PNGs and audio MP3s into a final MP4.

Uses MoviePy: loads each (PNG, MP3) pair, creates a clip with the audio,
adds fade transitions, concatenates all clips → single MP4.
"""

import os

import structlog
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
)

logger = structlog.get_logger(__name__)

OUTPUT_FPS = 24
FADE_DURATION = 0.5  # seconds


def compile_video(
    slide_paths: list[str],
    audio_paths: list[str],
    slide_durations: list[int],
    output_path: str,
) -> str:
    """Stitch slides and audio into a single MP4.

    Args:
        slide_paths: Ordered list of PNG slide file paths.
        audio_paths: Ordered list of MP3 audio file paths (one per slide).
        slide_durations: Target duration (seconds) for each slide.
        output_path: Full path for the output MP4.

    Returns:
        Path to the generated MP4 file.

    Raises:
        RuntimeError if compilation fails.
    """
    if not slide_paths:
        raise RuntimeError("No slide images provided for video compilation.")

    clips = []
    for i, (png, mp3) in enumerate(zip(slide_paths, audio_paths)):
        # Determine clip duration from audio (actual TTS length) or fallback to script value
        try:
            audio = AudioFileClip(mp3)
            duration = audio.duration
        except Exception as exc:
            logger.warning("Could not read audio duration, using script value", error=str(exc))
            duration = float(slide_durations[i]) if i < len(slide_durations) else 30.0

        # Build image clip with audio
        try:
            clip = ImageClip(png).set_duration(duration)
            if os.path.exists(mp3):
                clip = clip.set_audio(AudioFileClip(mp3).subclip(0, duration))
        except Exception as exc:
            logger.error("Failed to build clip", slide=png, error=str(exc))
            continue

        # Add fade-in and fade-out transitions
        clip = clip.fadein(FADE_DURATION).fadeout(FADE_DURATION)
        clips.append(clip)

    if not clips:
        raise RuntimeError("All clips failed to build — cannot compile video.")

    logger.info("Concatenating clips", count=len(clips))
    final = concatenate_videoclips(clips, method="compose")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    final.write_videofile(
        output_path,
        fps=OUTPUT_FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=output_path.replace(".mp4", "_temp_audio.m4a"),
        remove_temp=True,
        logger=None,  # Suppress MoviePy's verbose stdout
    )

    logger.info("Video compiled", output=output_path, clips=len(clips))
    return output_path
