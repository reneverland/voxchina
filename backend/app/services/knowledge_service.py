import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from loguru import logger
from typing import List, Dict, Any, Optional
import uuid
import json
import os
from datetime import datetime

# Configuration
QDRANT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "qdrant_data")
COLLECTION_NAME = "voxchina_knowledge"
# Default to local host if not specified, but try to respect env vars if any
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = "qwen3-embedding" # Corrected to match Ollama model name

class KnowledgeService:
    def __init__(self):
        # Ensure qdrant data directory exists
        os.makedirs(QDRANT_PATH, exist_ok=True)
        
        # Try to initialize Qdrant client, if it fails due to version incompatibility,
        # clean up and retry
        try:
            self.client = QdrantClient(path=QDRANT_PATH)
        except Exception as e:
            logger.warning(f"Failed to initialize Qdrant client (likely version incompatibility): {e}")
            logger.info("Cleaning up corrupted Qdrant data and reinitializing...")
            
            # Remove corrupted data directory
            import shutil
            try:
                shutil.rmtree(QDRANT_PATH)
                logger.info(f"Removed corrupted data directory: {QDRANT_PATH}")
            except Exception as cleanup_error:
                logger.error(f"Failed to remove data directory: {cleanup_error}")
                raise
            
            # Recreate directory and retry
            os.makedirs(QDRANT_PATH, exist_ok=True)
            self.client = QdrantClient(path=QDRANT_PATH)
            logger.info("Successfully reinitialized Qdrant client with clean data")
        
        # Detect embedding dimension dynamically first
        self.embedding_dimension = self._detect_embedding_dimension()
        self._ensure_collection()

    def _detect_embedding_dimension(self) -> int:
        """Detect the embedding dimension by making a test call"""
        try:
            test_vector = self._get_embedding("test")
            dimension = len(test_vector)
            logger.info(f"Detected embedding dimension: {dimension}")
            return dimension
        except Exception as e:
            logger.warning(f"Failed to detect embedding dimension, using default 4096: {e}")
            return 4096  # Default for qwen3-embedding:latest (7.6B model)
    
    def _ensure_collection(self):
        try:
            collections = self.client.get_collections()
            exists = any(c.name == COLLECTION_NAME for c in collections.collections)
            
            if exists:
                # Check if dimension matches
                try:
                    collection_info = self.client.get_collection(COLLECTION_NAME)
                    current_dim = collection_info.config.params.vectors.size
                    if current_dim != self.embedding_dimension:
                        logger.warning(f"Collection dimension mismatch: {current_dim} vs {self.embedding_dimension}. Recreating collection.")
                        self.client.delete_collection(COLLECTION_NAME)
                        exists = False
                    else:
                        logger.info(f"Collection {COLLECTION_NAME} already exists with correct dimension {current_dim}")
                except Exception as e:
                    logger.warning(f"Could not check collection dimension: {e}")
            
            if not exists:
                # Use the detected dimension
                logger.info(f"Creating collection {COLLECTION_NAME} with dimension {self.embedding_dimension}")
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=self.embedding_dimension, distance=Distance.COSINE),
                )
        except Exception as e:
            logger.error(f"Failed to ensure collection: {e}")

    def _get_embedding(self, text: str) -> List[float]:
        try:
            url = f"{OLLAMA_BASE_URL}/api/embeddings"
            logger.debug(f"[Embedding] Calling Ollama at {url} with model {EMBEDDING_MODEL}")
            logger.debug(f"[Embedding] Text length: {len(text)} chars")
            
            response = httpx.post(url, json={
                "model": EMBEDDING_MODEL,
                "prompt": text
            }, timeout=90.0)  # Increased timeout to 90s for very large texts
            
            if response.status_code == 200:
                data = response.json()
                embedding = data["embedding"]
                logger.debug(f"[Embedding] ✅ Success. Vector dimension: {len(embedding)}")
                return embedding
            else:
                logger.error(f"[Embedding] ❌ Ollama embedding failed with status {response.status_code}: {response.text}")
                raise Exception(f"Ollama error: {response.status_code} - {response.text}")
        except httpx.TimeoutException as e:
            logger.error(f"[Embedding] ❌ Timeout after 90s. Text might be too long or Ollama is slow.")
            raise Exception(f"Embedding timeout: Ollama took too long to respond. Text length: {len(text)} chars")
        except Exception as e:
            logger.error(f"[Embedding] ❌ Error: {e}")
            raise

    async def add_document(self, 
                           content: str, 
                           metadata: Dict[str, Any],
                           doc_id: Optional[str] = None) -> str:
        """
        Add a document to the knowledge base.
        Metadata should include: title, type (article/summary), source_file, created_at, etc.
        """
        try:
            logger.info(f"[KB Add] Starting to add document. Content length: {len(content)} chars")
            
            # Generate embedding vector
            logger.info(f"[KB Add] Generating embedding vector using {EMBEDDING_MODEL}...")
            import time
            start_time = time.time()
            vector = self._get_embedding(content)
            embedding_time = time.time() - start_time
            logger.info(f"[KB Add] Embedding generated successfully in {embedding_time:.2f}s. Vector dimension: {len(vector)}")
            
            if not doc_id:
                doc_id = str(uuid.uuid4())
            
            # Ensure metadata is flat or compatible
            if "created_at" not in metadata:
                metadata["created_at"] = datetime.now().isoformat()
            
            # Store full content in metadata for retrieval
            metadata["content"] = content
            
            logger.info(f"[KB Add] Saving to Qdrant collection '{COLLECTION_NAME}'...")
            point = PointStruct(
                id=doc_id,
                vector=vector,
                payload=metadata
            )
            
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=[point]
            )
            logger.info(f"[KB Add] ✅ Successfully added document {doc_id} to knowledge base. Title: {metadata.get('title', 'N/A')}")
            return doc_id
        except Exception as e:
            logger.error(f"[KB Add] ❌ Failed to add document: {e}")
            import traceback
            logger.error(f"[KB Add] Traceback: {traceback.format_exc()}")
            raise

    async def search_similar(self, query: str, limit: int = 5, score_threshold: float = 0.5) -> List[Dict[str, Any]]:
        try:
            vector = self._get_embedding(query)
            
            results = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=vector,
                limit=limit,
                score_threshold=score_threshold
            )
            
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                for hit in results
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def list_documents(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List documents sorted by created_at desc (if possible) or just scroll.
        Qdrant scroll is arbitrary order usually, but we can try.
        """
        try:
            # Scroll all (up to limit + offset) and sort in python for now as Qdrant scroll is simple
            # Ideally we use payload index for sorting but for small knowledge base Python sort is fine.
            # For efficiency in larger bases, we'd add an integer timestamp and use order_by.
            
            # Just simple scroll for now
            results, _ = self.client.scroll(
                collection_name=COLLECTION_NAME,
                limit=100, # Fetch more to sort
                with_payload=True,
                with_vectors=False
            )
            
            # Sort by created_at desc
            results.sort(key=lambda x: x.payload.get("created_at", ""), reverse=True)
            
            # Apply limit/offset
            paged = results[offset:offset+limit]
            
            return [
                {
                    "id": point.id,
                    "payload": point.payload
                }
                for point in paged
            ]
        except Exception as e:
            logger.error(f"List documents failed: {e}")
            return []

    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single document by ID
        """
        try:
            points = self.client.retrieve(
                collection_name=COLLECTION_NAME,
                ids=[doc_id],
                with_payload=True,
                with_vectors=False
            )
            
            if not points:
                return None
            
            point = points[0]
            return {
                "id": point.id,
                "payload": point.payload,
                "metadata": point.payload
            }
        except Exception as e:
            logger.error(f"Get document failed: {e}")
            return None

    async def delete_document(self, doc_id: str) -> bool:
        try:
            # Qdrant delete uses Filter
            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=[doc_id]
            )
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False

knowledge_service = KnowledgeService()
