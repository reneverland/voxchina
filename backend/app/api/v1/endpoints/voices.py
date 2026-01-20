from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Body
from typing import List, Optional
from app.models.schemas import VoiceResponse
from app.services.voice_service import voice_service
from app.api.v1.endpoints.auth import get_current_user
from loguru import logger
from pydantic import BaseModel

router = APIRouter()

class PreviewRequest(BaseModel):
    voice_id: Optional[str] = ""  # Allow empty string for default voice
    text: Optional[str] = None
    language: str = "zh"

class PreviewResponse(BaseModel):
    audio_url: str

@router.post("/upload", response_model=VoiceResponse)
async def upload_voice(name: str = Form(...), file: UploadFile = File(...), user: str = Depends(get_current_user)):
    """
    Upload a reference audio file to create a new voice clone.
    """
    try:
        content = await file.read()
        filename = file.filename or f"{name}.wav"
        
        voice = await voice_service.add_voice(name, content, filename)
        
        return voice
    except Exception as e:
        logger.error(f"Voice upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[VoiceResponse])
async def list_voices():
    """
    List all available cloned voices.
    """
    try:
        logger.info("[Voices API] Listing voices...")
        voices = voice_service.list_voices()
        logger.info(f"[Voices API] Found {len(voices)} voices")
        return voices
    except Exception as e:
        logger.error(f"[Voices API] Failed to list voices: {e}")
        import traceback
        logger.error(f"[Voices API] Traceback: {traceback.format_exc()}")
        # Return empty list instead of 500 error for better UX
        return []

@router.delete("/{voice_id}")
async def delete_voice(voice_id: str, user: str = Depends(get_current_user)):
    """
    Delete a voice.
    """
    success = voice_service.delete_voice(voice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Voice not found")
    return {"message": "Voice deleted"}

@router.post("/preview", response_model=PreviewResponse)
async def preview_voice(request: PreviewRequest):
    """
    Generate a preview audio for a specific voice.
    If voice_id is empty or not found, uses default base voice.
    """
    try:
        # Check if voice exists (allow empty voice_id for default voice)
        voice_id_to_use = None
        if request.voice_id:
            voice = voice_service.get_voice(request.voice_id)
            if not voice:
                logger.warning(f"Voice {request.voice_id} not found, using default voice")
            else:
                voice_id_to_use = request.voice_id
        
        text = request.text
        if not text:
            if request.language == "zh":
                text = "你好，欢迎使用 VoxChina 的克隆声音模型，这是一段测试语音。"
            else:
                text = "Hello, welcome to use VoxChina's cloned voice model. This is a test audio."
                
        # Generate audio
        import uuid
        filename = f"preview_{voice_id_to_use or 'default'}_{uuid.uuid4()}.wav"
        audio_path = None
        try:
            logger.info(f"[Voices API] Generating audio preview: text_len={len(text)}, voice_id={voice_id_to_use}, filename={filename}")
            from app.services.tts_service import tts_service
            audio_path = tts_service.generate_audio(text, filename, voice_id=voice_id_to_use)
            
            if not audio_path:
                logger.error(f"[Voices API] ❌ TTS service returned None (generation failed)")
                raise HTTPException(
                    status_code=500, 
                    detail="Audio generation failed. Please check if TTS models are properly loaded. Check server logs for details."
                )
                
            logger.info(f"[Voices API] ✅ Audio generated successfully: {audio_path}")
            return {"audio_url": f"/static/audio/{filename}"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[Voices API] ❌ TTS service error: {e}")
            import traceback
            logger.error(f"[Voices API] Traceback: {traceback.format_exc()}")
            
            # Provide more specific error messages
            error_detail = f"Audio generation failed: {str(e)}"
            if "CUDA" in str(e) or "GPU" in str(e):
                error_detail += " (GPU/CUDA error - check GPU availability)"
            elif "model" in str(e).lower() or "checkpoint" in str(e).lower():
                error_detail += " (Model loading error - check if TTS models are installed)"
            elif "memory" in str(e).lower():
                error_detail += " (Memory error - insufficient RAM/VRAM)"
                
            raise HTTPException(status_code=500, detail=error_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preview generation failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
