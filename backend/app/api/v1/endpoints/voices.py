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
    logger.info(f"[Voice Upload] ========== START ==========")
    logger.info(f"[Voice Upload] Request received: name={name}, user={user}")
    
    try:
        logger.info(f"[Voice Upload] Step 1: Checking TTS service status...")
        # 检查 TTS 服务是否已加载
        from app.services.tts_service import tts_service
        logger.info(f"[Voice Upload] TTS service imported. loaded={tts_service.loaded}")
        logger.info(f"[Voice Upload] Voice service converter: {voice_service.tone_color_converter is not None}")
        
        if not tts_service.loaded or voice_service.tone_color_converter is None:
            logger.warning(f"[Voice Upload] TTS models not loaded yet. loaded={tts_service.loaded}, converter={voice_service.tone_color_converter is not None}")
            raise HTTPException(
                status_code=503, 
                detail="语音处理模型正在加载中，请稍等 1-2 分钟后再试。Voice processing models are loading, please wait 1-2 minutes and try again."
            )
        
        logger.info(f"[Voice Upload] Step 2: Reading file content...")
        content = await file.read()
        filename = file.filename or f"{name}.wav"
        logger.info(f"[Voice Upload] File read complete: filename={filename}, size={len(content)} bytes")
        
        logger.info(f"[Voice Upload] Step 3: Processing voice: name={name}, file={filename}, size={len(content)} bytes, user={user}")
        
        logger.info(f"[Voice Upload] Step 4: Calling voice_service.add_voice()...")
        voice = await voice_service.add_voice(name, content, filename)
        logger.info(f"[Voice Upload] Step 5: Voice service completed successfully")
        
        logger.info(f"[Voice Upload] ✅ Voice uploaded successfully: {voice['id']}")
        logger.info(f"[Voice Upload] ========== END SUCCESS ==========")
        return voice
    except HTTPException as he:
        logger.error(f"[Voice Upload] ❌ HTTPException: {he.status_code} - {he.detail}")
        logger.info(f"[Voice Upload] ========== END HTTP ERROR ==========")
        raise
    except Exception as e:
        logger.error(f"[Voice Upload] ❌ Exception type: {type(e).__name__}")
        logger.error(f"[Voice Upload] ❌ Exception message: {e}")
        import traceback
        logger.error(f"[Voice Upload] ❌ Full traceback:\n{traceback.format_exc()}")
        logger.info(f"[Voice Upload] ========== END EXCEPTION ==========")
        
        # 提供更友好的错误信息
        error_msg = str(e)
        if "not loaded" in error_msg.lower() or "models are not" in error_msg.lower():
            raise HTTPException(
                status_code=503, 
                detail="语音处理模型尚未加载完成，请稍等片刻后再试。Voice processing models are not ready, please try again in a moment."
            )
        else:
            raise HTTPException(status_code=500, detail=f"声音上传失败：{error_msg}。Voice upload failed: {error_msg}")

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


class GenerateArticleRequest(BaseModel):
    """文章生成请求"""
    prompt: str  # 用户输入的提示/主题
    style: str = "professional"  # 风格: professional, casual, academic
    length: str = "medium"  # 长度: short(500字), medium(1000字), long(2000字)
    language: str = "zh"


class GenerateArticleResponse(BaseModel):
    """文章生成响应"""
    article: str
    word_count: int


@router.post("/generate-article", response_model=GenerateArticleResponse)
async def generate_article(
    request: GenerateArticleRequest,
    user: str = Depends(get_current_user)
):
    """
    根据用户输入的提示生成文章
    
    可用于生成口播稿、演讲稿、文章等，然后用克隆的声音朗读
    """
    try:
        from app.services.llm_service import llm_service
        
        logger.info(f"[Generate Article] User: {user}, Prompt: {request.prompt[:50]}...")
        
        # 根据长度设置字数目标
        length_map = {
            "short": 500,
            "medium": 1000,
            "long": 2000
        }
        target_words = length_map.get(request.length, 1000)
        
        # 根据风格设置语气
        style_map = {
            "professional": "专业、正式、客观",
            "casual": "轻松、亲切、口语化",
            "academic": "学术、严谨、引用数据"
        }
        style_desc = style_map.get(request.style, "专业、正式")
        
        # 构建 prompt
        if request.language == "zh":
            prompt = f"""请根据以下主题/提示，撰写一篇适合口播朗读的文章。

【主题/提示】
{request.prompt}

【要求】
1. 字数：约 {target_words} 字
2. 风格：{style_desc}
3. 结构：有清晰的开头、主体和结尾
4. 语言：中文，适合朗读，多用短句
5. 内容：基于事实，避免虚构

请直接输出文章内容，不要包含标题或其他元信息。"""
        else:
            prompt = f"""Please write an article suitable for voice broadcast based on the following topic/prompt.

【Topic/Prompt】
{request.prompt}

【Requirements】
1. Word count: approximately {target_words} words
2. Style: {style_desc}
3. Structure: clear introduction, body, and conclusion
4. Language: English, suitable for reading aloud, use short sentences
5. Content: fact-based, avoid fiction

Please output the article content directly, without title or other meta information."""
        
        # 调用 LLM 生成文章
        article = await llm_service._generate_with_provider(
            prompt=prompt,
            timeout=120.0
        )
        
        # 清理文章
        article = article.strip()
        
        # 计算字数
        if request.language == "zh":
            word_count = len(article.replace(" ", "").replace("\n", ""))
        else:
            word_count = len(article.split())
        
        logger.info(f"[Generate Article] Generated article with {word_count} words")
        
        return GenerateArticleResponse(
            article=article,
            word_count=word_count
        )
        
    except Exception as e:
        logger.error(f"[Generate Article] Failed: {e}")
        import traceback
        logger.error(f"[Generate Article] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"文章生成失败: {str(e)}")
