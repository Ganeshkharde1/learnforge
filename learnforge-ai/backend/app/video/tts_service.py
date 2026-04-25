"""TTS Service — Google Cloud Text-to-Speech for slide narration.

Uses WaveNet voice en-US-Wavenet-D as specified in MASTER_PLAN Section 11.5.
Generates one MP3 file per slide narration.
"""

import os

import structlog
from google.cloud import texttospeech

from app.config import settings

logger = structlog.get_logger(__name__)


class TTSService:
    """Synthesizes speech for video slide narration using Cloud TTS."""

    def __init__(self) -> None:
        self._client: texttospeech.TextToSpeechClient | None = None

    @property
    def client(self) -> texttospeech.TextToSpeechClient:
        if self._client is None:
            self._client = texttospeech.TextToSpeechClient()
        return self._client

    def synthesize_slide(self, text: str, output_path: str) -> str:
        """Synthesize narration for a single slide.

        Args:
            text: The narration text to speak.
            output_path: Full path for the output MP3 file.

        Returns:
            Path to the generated MP3 file.
        """
        if not text.strip():
            # Generate a short silence placeholder
            return self._generate_silence(output_path)

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=settings.TTS_LANGUAGE_CODE,
            name=settings.TTS_VOICE_NAME,
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95,  # Slightly slower for clarity
            pitch=0.0,
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.audio_content)

        logger.info(
            "TTS synthesized",
            chars=len(text),
            output=output_path,
            bytes=len(response.audio_content),
        )
        return output_path

    def synthesize_all_slides(
        self, slides: list[dict], audio_dir: str
    ) -> list[str]:
        """Synthesize audio for all slides in the script.

        Args:
            slides: List of slide dicts with 'narration' field.
            audio_dir: Directory to write audio files.

        Returns:
            Ordered list of MP3 file paths (one per slide).
        """
        os.makedirs(audio_dir, exist_ok=True)
        audio_paths = []

        for i, slide in enumerate(slides):
            narration = slide.get("narration", "")
            output_path = os.path.join(audio_dir, f"slide_{i+1:03d}.mp3")

            try:
                path = self.synthesize_slide(narration, output_path)
                audio_paths.append(path)
            except Exception as exc:
                logger.error(
                    "TTS failed for slide, using silence",
                    slide_num=i + 1,
                    error=str(exc),
                )
                audio_paths.append(self._generate_silence(output_path))

        return audio_paths

    @staticmethod
    def _generate_silence(output_path: str, duration_seconds: float = 3.0) -> str:
        """Generate a silent MP3 as a fallback using pydub or ffmpeg.

        Args:
            output_path: Where to write the silence MP3.
            duration_seconds: Length of silence.

        Returns:
            Path to the silence MP3.
        """
        import subprocess

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-f", "lavfi",
                    "-i", f"anullsrc=r=22050:cl=mono",
                    "-t", str(duration_seconds),
                    "-q:a", "9",
                    "-acodec", "libmp3lame",
                    output_path,
                ],
                capture_output=True,
                timeout=30,
            )
        except Exception:
            # Last resort: write a minimal valid MP3 header
            with open(output_path, "wb") as f:
                f.write(b"\xff\xfb\x90\x00" * 1000)

        return output_path


tts_service = TTSService()
