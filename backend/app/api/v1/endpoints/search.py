from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest, SearchResponse, SearchResultItem
from app.services.llm_service import llm_service
from app.services.vector_service import vector_service
from loguru import logger

router = APIRouter()

@router.post("/query", response_model=SearchResponse)
async def search_and_answer(request: SearchRequest):
    """
    Semantic Search + RAG Q&A
    """
    try:
        # 1. Semantic Search in Qdrant
        # Retrieve top K relevant chunks
        results = await vector_service.search_similar(request.query, limit=request.limit)
        
        sources = []
        context_texts = []
        
        for hit in results:
            payload = hit.payload or {}
            sources.append(SearchResultItem(
                id=str(hit.id),
                title=payload.get("title", "Untitled"),
                summary=payload.get("summary", ""),
                score=hit.score
            ))
            # Use full content for context if available, otherwise summary
            content = payload.get("content", "")
            if not content:
                content = payload.get("summary", "")
            if content:
                context_texts.append(content)

        # 2. Generate Answer
        if not context_texts:
            if request.language == "en":
                answer = "Sorry, no relevant content found in the knowledge base."
            else:
                answer = "抱歉，知识库中暂时没有相关内容。"
        else:
            answer = await llm_service.answer_query(request.query, context_texts, language=request.language)
        
        return SearchResponse(
            answer=answer,
            sources=sources
        )

    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

