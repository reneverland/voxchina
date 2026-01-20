from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import TrendingRequest, TrendingResponse
from app.services.llm_service import llm_service
from app.services.vector_service import vector_service
from app.services.web_search_service import web_search_service
from app.api.v1.endpoints.auth import get_current_user
from loguru import logger

router = APIRouter()

@router.post("/generate", response_model=TrendingResponse)
async def generate_trending_content(request: TrendingRequest, user: str = Depends(get_current_user)):
    """
    Generate trending post and optional video script.
    1. Search web for topic
    2. Search local DB for context
    3. Generate Post
    4. (Optional) Generate Video Script
    """
    try:
        logger.info(f"Processing trending topic: {request.topic}")
        
        # 1. Web Search
        web_results = web_search_service.search(request.topic)
        
        # 2. Local Context
        local_results = await vector_service.search_similar(request.topic, limit=3)
        local_context = [r.payload.get("content", "") for r in local_results if r.payload]
        
        # 3. Generate Post
        post_content = await llm_service.generate_trending_post(
            request.topic,
            web_results,
            local_context,
            language=request.language
        )
        
        # 4. Video Script (Optional)
        script_content = None
        if request.generate_script:
            script_content = await llm_service.generate_video_script(post_content, language=request.language)
            
        return TrendingResponse(
            post_content=post_content,
            script_content=script_content
        )
        
    except Exception as e:
        logger.error(f"Error generating trending content: {e}")
        raise HTTPException(status_code=500, detail=str(e))
