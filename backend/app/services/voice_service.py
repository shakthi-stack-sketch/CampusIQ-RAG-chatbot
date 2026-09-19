import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

class VoiceService:
    """
    Local Voice Service for CampusIQ:
    - Speech-to-Text: Modular Whisper transcription
    - Text-to-Speech: Modular audio synthesis architecture
    """

    def __init__(self):
        self._whisper_model = None

    def _get_whisper_model(self):
        """Lazy loader for Whisper model."""
        if self._whisper_model is None:
            try:
                import whisper
                from backend.app.config import WHISPER_MODEL_SIZE
                print(f"[VoiceService] Loading Whisper model ({WHISPER_MODEL_SIZE})...")
                self._whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
            except Exception as e:
                print(f"[VoiceService] Whisper unavailable: {e}")
                return None
        return self._whisper_model

    def transcribe_audio_file(self, file_bytes: bytes, filename: str = "audio.wav") -> Dict[str, Any]:
        """Transcribe uploaded audio bytes using local Whisper."""
        temp_dir = tempfile.gettempdir()
        temp_audio_path = os.path.join(temp_dir, f"campusiq_{filename}")

        try:
            with open(temp_audio_path, "wb") as f:
                f.write(file_bytes)

            model = self._get_whisper_model()
            if model is not None:
                result = model.transcribe(temp_audio_path)
                transcribed_text = result.get("text", "").strip()
                return {
                    "success": True,
                    "text": transcribed_text,
                    "engine": "local_whisper"
                }
            else:
                return {
                    "success": False,
                    "text": "",
                    "error": "Whisper is not initialized. Please ensure whisper and ffmpeg are installed, or use browser speech recognition."
                }
        except Exception as e:
            print(f"[VoiceService] Transcription error: {e}")
            return {
                "success": False,
                "text": "",
                "error": f"Audio processing failed: {str(e)}"
            }
        finally:
            if os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                except Exception:
                    pass

    def synthesize_speech(self, text: str) -> Dict[str, Any]:
        """
        Modular Text-to-Speech interface.
        Configurable to return synthesized audio or instruct client browser synthesis.
        """
        return {
            "success": True,
            "text": text,
            "action": "client_speech_synthesis",
            "message": "TTS architecture active. Use client Web Speech API or configure local engine."
        }

voice_service = VoiceService()
