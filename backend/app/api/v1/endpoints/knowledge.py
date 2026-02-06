from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.services.knowledge_service import knowledge_service
import docx
import PyPDF2
import io

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

class TagCreate(BaseModel):
    name: str

class TagRecommendationRequest(BaseModel):
    text: str
    limit: int = 5

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

@router.get("/tags", response_model=List[str])
async def get_tags():
    """Get all available tags"""
    try:
        return await knowledge_service.get_all_tags()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tags", response_model=Dict[str, str])
async def add_tag(tag: TagCreate):
    """Add a new tag to the knowledge base"""
    try:
        tag_id = knowledge_service.add_tag(tag.name)
        return {"id": tag_id, "name": tag.name, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend-tags", response_model=List[str])
async def recommend_tags(request: TagRecommendationRequest):
    """Recommend tags based on text content"""
    try:
        return await knowledge_service.recommend_tags(request.text, request.limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and parse a document file"""
    try:
        content = await file.read()
        
        # Parse based on file type
        text_content = ""
        title = file.filename
        
        if file.filename.endswith('.pdf'):
            # Parse PDF
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
        
        elif file.filename.endswith('.docx'):
            # Parse DOCX
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            for para in doc.paragraphs:
                text_content += para.text + "\n"
        
        elif file.filename.endswith('.txt'):
            # Parse TXT
            text_content = content.decode('utf-8', errors='ignore')
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Extract title from first line or use filename
        lines = text_content.strip().split('\n')
        if lines:
            title = lines[0][:100] if len(lines[0]) > 0 else file.filename
        
        return {
            "title": title,
            "content": text_content,
            "filename": file.filename
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")

@router.post("/documents", response_model=Dict[str, str])
async def create_document(doc: DocumentCreate):
    """Create a new document in the knowledge base (alias for /add)"""
    try:
        doc_id = await knowledge_service.add_document(doc.content, doc.metadata)
        return {"id": doc_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
