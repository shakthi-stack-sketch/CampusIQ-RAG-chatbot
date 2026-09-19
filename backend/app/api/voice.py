from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from backend.app.services.voice_service import voice_service

router = APIRouter(prefix="/api/voice", tags=["Voice"])

class TTSRequest(BaseModel):
    text: str

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe user spoken question using local Whisper."""
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file received")
        result = voice_service.transcribe_audio_file(audio_bytes, filename=file.filename or "recording.webm")
        return result
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": f"Audio processing error: {str(e)}"
        }

@router.post("/tts")
def text_to_speech(req: TTSRequest):
    """Modular TTS endpoint for vocal responses."""
    return voice_service.synthesize_speech(req.text)
