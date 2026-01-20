from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.services.knowledge_service import knowledge_service

router = APIRouter()

class DocumentCreate(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class DocumentResponse(BaseModel):
    id: str
    payload: Dict[str, Any]
    score: Optional[float] = None

class SearchQuery(BaseModel):
    query: str
    limit: int = 12
    offset: int = 0

@router.post("/add", response_model=Dict[str, str])
async def add_document(doc: DocumentCreate):
    """Add a document to the knowledge base"""
    try:
        doc_id = await knowledge_service.add_document(doc.content, doc.metadata)
        return {"id": doc_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_documents(limit: int = 20, offset: int = 0):
    """List documents in the knowledge base with pagination"""
    try:
        # Get more documents to count total
        all_docs = await knowledge_service.list_documents(limit=100, offset=0)
        total = len(all_docs)
        
        # Apply pagination
        docs = all_docs[offset:offset+limit]
        
        return {
            "items": docs,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_documents(query: SearchQuery):
    """Search for similar documents with pagination"""
    try:
        offset = getattr(query, 'offset', 0)
        results = await knowledge_service.search_similar(query.query, query.limit)
        
        return {
            "items": results,
            "total": len(results),
            "limit": query.limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    try:
        success = await knowledge_service.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found or failed to delete")
        return {"status": "success", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
