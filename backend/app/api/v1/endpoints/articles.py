import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from app.models.schemas import ArticleRequest, ArticleResponse, ArticleListItem, IntegrationRequest, IntegrationResponse
from app.services.llm_service import llm_service
from app.services.vector_service import vector_service
from app.api.v1.endpoints.auth import get_current_user
from loguru import logger

router = APIRouter()

async def save_to_vector_db(content: str, summary: str, title: str = None):
    try:
        logger.info("Saving article to Vector DB...")
        metadata = {
            "summary": summary,
            "title": title or "Untitled",
            "content": content,  # Store full content for retrieval/integration
            "type": "article",
            "created_at": str(uuid.uuid4())
        }
        await vector_service.add_article(content, metadata)
        logger.info("Article saved to Vector DB.")
    except Exception as e:
        logger.error(f"Failed to save to vector DB: {e}")

@router.post("/summarize-audio", response_model=ArticleResponse)
async def process_article(request: ArticleRequest, background_tasks: BackgroundTasks, user: str = Depends(get_current_user)):
    """
    1. Generate Summary (Qwen3)
    2. Generate Audio (OpenVoice/MeloTTS)
    3. Save to Vector DB (Background)
    4. Return results
    """
    try:
        # 1. Summary
        logger.info("Generating summary...")
        summary = await llm_service.generate_summary(request.content, language=request.language)
        
        # 2. Audio
        logger.info("Generating audio...")
        filename = f"{uuid.uuid4()}.wav"
        audio_path = None
        try:
            from app.services.tts_service import tts_service
            audio_path = tts_service.generate_audio(summary, filename, voice_id=request.voice_id)
        except Exception as e:
            logger.warning(f"TTS service not available: {e}")
        
        if audio_path:
            audio_url = f"/static/audio/{filename}"
        else:
            audio_url = "" # Handle empty audio gracefully
        
        # 3. Background Task: Save to Qdrant
        background_tasks.add_task(save_to_vector_db, request.content, summary, request.title)
        
        return ArticleResponse(
            summary=summary,
            audio_url=audio_url,
            message="Success" if audio_path else "Summary generated, but Audio failed (Check server logs)"
        )

    except Exception as e:
        logger.error(f"Error processing article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[ArticleListItem])
async def list_articles(limit: int = 20):
    """List recent articles from Qdrant"""
    # Note: Listing articles is usually public, but let's leave it public for now or protect if needed.
    # For now, let's keep it public for dashboard visibility, or add auth if strictly private.
    articles = await vector_service.list_articles(limit=limit)
    return articles

@router.post("/integrate", response_model=IntegrationResponse)
async def integrate_articles(request: IntegrationRequest, user: str = Depends(get_current_user)):
    """
    Integrate multiple articles into one.
    """
    try:
        # 1. Retrieve contents
        contents = await vector_service.get_articles_by_ids(request.article_ids)
        if not contents:
            raise HTTPException(status_code=404, detail="No articles found with provided IDs")
        
        # 2. Integrate using LLM
        integrated_text = await llm_service.integrate_articles(
            contents, 
            max_words=request.max_words, 
            focus=request.focus,
            language=request.language
        )
        
        # 3. (Optional) Generate Audio for integrated text?
        filename = f"integrated_{uuid.uuid4()}.wav"
        audio_path = None
        try:
            from app.services.tts_service import tts_service
            audio_path = tts_service.generate_audio(integrated_text, filename, voice_id=request.voice_id)
        except Exception as e:
            logger.warning(f"TTS service not available: {e}")
        
        if audio_path:
            audio_url = f"/static/audio/{filename}"
        else:
            audio_url = None
        
        return IntegrationResponse(
            integrated_content=integrated_text,
            audio_url=audio_url
        )
        
    except Exception as e:
        logger.error(f"Error integrating articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))
