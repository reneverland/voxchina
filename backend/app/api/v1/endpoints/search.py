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
        # Check if vector_service is properly initialized
        if not hasattr(vector_service, 'client') or vector_service.client is None:
            logger.error("Vector service is not initialized")
            if request.language == "en":
                error_msg = "Search service is currently unavailable. Please ensure the vector database is running."
            else:
                error_msg = "搜索服务当前不可用，请确保向量数据库正在运行。"
            raise HTTPException(status_code=503, detail=error_msg)
        
        # 1. Semantic Search in Qdrant
        # Retrieve top K relevant chunks
        results = await vector_service.search_similar(request.query, limit=request.limit)
        
        sources = []
        context_texts = []
        
        for hit in results:
            payload = hit.payload or {}
            
            # Handle different payload structures
            # For knowledge_base collection: uses 'text' field
            # For other collections: uses 'title', 'summary', 'content'
            text_content = payload.get("text", "")
            title = payload.get("title", "")
            summary = payload.get("summary", "")
            content = payload.get("content", "")
            
            # If using knowledge_base structure (has 'text' field)
            if text_content:
                # Extract title from first line or use entry_id
                first_line = text_content.split('\n')[0][:100] if text_content else ""
                display_title = first_line if first_line else f"Document {payload.get('entry_id', 'Unknown')}"
                display_summary = text_content[:300] + "..." if len(text_content) > 300 else text_content
                context_texts.append(text_content)
            else:
                # Use standard structure
                display_title = title if title else "Untitled"
                display_summary = summary if summary else content[:300] if content else ""
                if content:
                    context_texts.append(content)
                elif summary:
                    context_texts.append(summary)
            
            sources.append(SearchResultItem(
                id=str(hit.id),
                title=display_title,
                summary=display_summary,
                score=hit.score
            ))

        # 2. Generate Answer
        if not context_texts:
            if request.language == "en":
                answer = "Sorry, no relevant content found in the knowledge base. Try uploading some documents first."
            else:
                answer = "抱歉，知识库中暂时没有相关内容。请先上传一些文档到知识库。"
        else:
            answer = await llm_service.answer_query(request.query, context_texts, language=request.language)
        
        return SearchResponse(
            answer=answer,
            sources=sources
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return user-friendly error message
        if request.language == "en":
            error_msg = f"Search failed: {str(e)}. Please try again or contact support."
        else:
            error_msg = f"搜索失败：{str(e)}。请重试或联系技术支持。"
        raise HTTPException(status_code=500, detail=error_msg)

