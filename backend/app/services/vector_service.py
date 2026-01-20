from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.core.config import settings
from loguru import logger
import httpx

class VectorService:
    def __init__(self):
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = "articles"
        self.embedding_model = settings.OLLAMA_EMBEDDING_MODEL 
        self._ensure_collection()
    def _ensure_collection(self):
        try:
            collections = self.client.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)
            
            if not exists:
                vector_size = self._get_embedding_dim()
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
                )
                logger.info(f"Created Qdrant collection '{self.collection_name}' with dim {vector_size}")
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection: {e}")
    

    def _get_embedding_dim(self) -> int:
        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{settings.OLLAMA_HOST}/api/embeddings",
                    json={"model": self.embedding_model, "prompt": "test"},
                    timeout=10.0
                )
                if resp.status_code == 200:
                    embedding = resp.json().get("embedding", [])
                    return len(embedding)
        except Exception as e:
            logger.warning(f"Could not determine embedding dim: {e}")
        return 4096 

    async def get_embedding(self, text: str) -> list[float]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OLLAMA_HOST}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                }
            )
            if response.status_code != 200:
                logger.error(f"Embedding failed: {response.text}")
                return []
            return response.json().get("embedding", [])

    async def search_similar(self, query: str, limit: int = 5):
        vector = await self.get_embedding(query)
        if not vector:
            return []
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit
        )
        return results

    async def add_article(self, content: str, metadata: dict):
        vector = await self.get_embedding(content)
        if not vector:
            return
            
        import uuid
        point_id = str(uuid.uuid4())
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=metadata
                )
            ]
        )

    async def list_articles(self, limit: int = 20, offset: int = 0):
        """
        List articles using scroll API.
        """
        try:
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            articles = []
            for point in results:
                articles.append({
                    "id": point.id,
                    "title": point.payload.get("title", "Untitled"),
                    "summary": point.payload.get("summary", ""),
                    "content": point.payload.get("content", "")
                })
            return articles
        except Exception as e:
            logger.error(f"List articles failed (maybe collection not ready): {e}")
            return []

    async def get_articles_by_ids(self, ids: list[str]):
        points = self.client.retrieve(
            collection_name=self.collection_name,
            ids=ids,
            with_payload=True,
            with_vectors=False
        )
        return [p.payload.get("content", "") for p in points if p.payload]
    

vector_service = VectorService()
