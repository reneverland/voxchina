import httpx
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.services.qdrant_singleton import qdrant_singleton
from loguru import logger
from typing import List, Dict, Any, Optional
import uuid
import json
import os
from datetime import datetime

# Configuration
COLLECTION_NAME = "voxchina"  # VoxChina dedicated collection
TAG_COLLECTION_NAME = "voxchina_tags"  # Dedicated collection for tags
# Default to local host if not specified, but try to respect env vars if any
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = "qwen3-embedding" # Corrected to match Ollama model name

DEFAULT_TAGS = [
    "金融系统", "货币政策", "环境经济", "劳动力市场", "人工智能", 
    "环境保护", "养老金体系", "粤港澳大湾区", "教育", "供应链", 
    "收入分配", "房市经济", "城市发展", "产业政策", "就业市场", 
    "国际贸易与投资", "宏观经济政策", "人口结构与老龄化", "社会保障", 
    "城乡融合发展", "消费与内需", "财税体制改革", "国企改革", 
    "资本市场", "地方政府", "地缘政治", "一带一路"
]

class KnowledgeService:
    def __init__(self):
        """初始化知识库服务，支持优雅降级"""
        self.initialized = False
        self.client = None
        self.embedding_dimension = 4096  # Default
        self.init_error = None
        
        try:
            # Use singleton Qdrant client to avoid concurrent access issues
            self.client = qdrant_singleton.get_client()
            logger.info(f"✅ KnowledgeService using shared Qdrant client")
            
            # Detect embedding dimension dynamically first
            self.embedding_dimension = self._detect_embedding_dimension()
            self._ensure_collection()
            self._ensure_tag_collection()
            self._init_default_tags()
            
            # Mark as successfully initialized
            self.initialized = True
            logger.info("✅ KnowledgeService initialized successfully")
            
        except Exception as e:
            # 记录错误但不抛出，允许服务在降级模式下运行
            self.init_error = str(e)
            logger.error(f"❌ KnowledgeService initialization failed: {e}")
            logger.warning("⚠️ KnowledgeService will run in degraded mode (read-only/empty responses)")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _check_initialized(self, operation_name: str = "操作"):
        """检查服务是否已初始化，如果未初始化则抛出友好的异常"""
        if not self.initialized:
            error_msg = f"知识库服务未初始化，无法执行{operation_name}"
            if self.init_error:
                error_msg += f"。初始化错误：{self.init_error}"
            logger.warning(f"⚠️ {error_msg}")
            raise RuntimeError(error_msg)

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

    def _ensure_tag_collection(self):
        """Ensure the tags collection exists"""
        try:
            collections = self.client.get_collections()
            exists = any(c.name == TAG_COLLECTION_NAME for c in collections.collections)
            
            if exists:
                try:
                    collection_info = self.client.get_collection(TAG_COLLECTION_NAME)
                    current_dim = collection_info.config.params.vectors.size
                    if current_dim != self.embedding_dimension:
                        logger.warning(f"Tag Collection dimension mismatch: {current_dim} vs {self.embedding_dimension}. Recreating collection.")
                        self.client.delete_collection(TAG_COLLECTION_NAME)
                        exists = False
                    else:
                        logger.info(f"Collection {TAG_COLLECTION_NAME} already exists")
                except Exception as e:
                    logger.warning(f"Could not check tag collection dimension: {e}")
            
            if not exists:
                logger.info(f"Creating collection {TAG_COLLECTION_NAME}")
                self.client.create_collection(
                    collection_name=TAG_COLLECTION_NAME,
                    vectors_config=VectorParams(size=self.embedding_dimension, distance=Distance.COSINE),
                )
        except Exception as e:
            logger.error(f"Failed to ensure tag collection: {e}")

    def _init_default_tags(self):
        """Initialize default tags if collection is empty"""
        try:
            # Check if empty
            count_result = self.client.count(collection_name=TAG_COLLECTION_NAME)
            if count_result.count == 0:
                logger.info("Initializing default tags...")
                for tag in DEFAULT_TAGS:
                    self.add_tag(tag)
                logger.info(f"Initialized {len(DEFAULT_TAGS)} default tags")
        except Exception as e:
            logger.error(f"Failed to init default tags: {e}")

    def add_tag(self, tag_name: str) -> str:
        """Add a single tag to the database"""
        try:
            # Check if already exists (by exact name match in payload)
            # This is a simple check, for strict uniqueness we might need scroll
            
            vector = self._get_embedding(tag_name)
            tag_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, tag_name)) # Deterministic ID based on name
            
            point = PointStruct(
                id=tag_id,
                vector=vector,
                payload={"name": tag_name, "type": "tag", "created_at": datetime.now().isoformat()}
            )
            
            self.client.upsert(
                collection_name=TAG_COLLECTION_NAME,
                points=[point]
            )
            return tag_id
        except Exception as e:
            logger.error(f"Failed to add tag {tag_name}: {e}")
            raise

    async def recommend_tags(self, text: str, limit: int = 5) -> List[str]:
        """Recommend tags based on text semantic similarity"""
        self._check_initialized("推荐标签")
        try:
            vector = self._get_embedding(text)
            
            response = self.client.query_points(
                collection_name=TAG_COLLECTION_NAME,
                query=vector,
                limit=limit,
                with_payload=True
            )
            
            # Extract points from QueryResponse
            points = response.points if hasattr(response, 'points') else []
            
            return [hit.payload["name"] for hit in points if "name" in hit.payload]
        except Exception as e:
            logger.error(f"Failed to recommend tags: {e}")
            return []

    async def get_all_tags(self) -> List[str]:
        """Get all available tags"""
        self._check_initialized("获取标签")
        try:
            results, _ = self.client.scroll(
                collection_name=TAG_COLLECTION_NAME,
                limit=1000,
                with_payload=True,
                with_vectors=False
            )
            # Sort alphabetically for better UX
            tags = [point.payload["name"] for point in results if "name" in point.payload]
            tags.sort()
            return tags
        except Exception as e:
            logger.error(f"Failed to get all tags: {e}")
            return []

    def _get_embedding(self, text: str) -> List[float]:
        """
        获取文本的 embedding 向量。
        对于长文本，会自动截断到安全长度以避免超出模型的 context length 限制。
        """
        try:
            url = f"{OLLAMA_BASE_URL}/api/embeddings"
            
            # 限制文本长度以避免超出 context length
            # 大多数 embedding 模型的 context length 在 2048-8192 tokens
            # 保守估计 1 token ≈ 2-3 个字符（中文）或 4 个字符（英文）
            MAX_CHARS = 6000  # 安全的字符数限制
            
            original_length = len(text)
            if original_length > MAX_CHARS:
                # 截断文本，保留开头和结尾部分以保持语义完整性
                head_chars = int(MAX_CHARS * 0.7)  # 70% 给开头
                tail_chars = int(MAX_CHARS * 0.3)  # 30% 给结尾
                text = text[:head_chars] + "\n...\n" + text[-tail_chars:]
                logger.warning(f"[Embedding] Text truncated from {original_length} to {len(text)} chars to fit context length")
            
            logger.debug(f"[Embedding] Calling Ollama at {url} with model {EMBEDDING_MODEL}")
            logger.debug(f"[Embedding] Text length: {len(text)} chars (original: {original_length})")
            
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
                error_text = response.text
                logger.error(f"[Embedding] ❌ Ollama embedding failed with status {response.status_code}: {error_text}")
                
                # 如果仍然超出长度，进一步截断并重试
                if "context length" in error_text.lower() or "input length" in error_text.lower():
                    logger.warning(f"[Embedding] Context length exceeded, retrying with shorter text...")
                    shorter_text = text[:3000]  # 进一步截断
                    retry_response = httpx.post(url, json={
                        "model": EMBEDDING_MODEL,
                        "prompt": shorter_text
                    }, timeout=90.0)
                    
                    if retry_response.status_code == 200:
                        data = retry_response.json()
                        embedding = data["embedding"]
                        logger.info(f"[Embedding] ✅ Retry success with truncated text ({len(shorter_text)} chars)")
                        return embedding
                
                raise Exception(f"Ollama error: {response.status_code} - {error_text}")
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
        self._check_initialized("添加文档")
        
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

    async def search_similar(self, query: str, limit: int = 5, score_threshold: float = 0.3) -> List[Dict[str, Any]]:
        if not self.initialized:
            logger.warning("⚠️ KnowledgeService not initialized, returning empty search results")
            return []
        
        try:
            vector = self._get_embedding(query)
            
            # Use query_points method for newer Qdrant versions
            # Note: score_threshold filtering happens after retrieval
            response = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=vector,
                limit=limit,
                with_payload=True
            )
            
            # Extract points from QueryResponse
            points = response.points if hasattr(response, 'points') else []
            
            # Filter by score threshold
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                for hit in points
                if hit.score >= score_threshold
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def list_documents(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List documents sorted by created_at desc (if possible) or just scroll.
        Qdrant scroll is arbitrary order usually, but we can try.
        """
        if not self.initialized:
            logger.warning("⚠️ KnowledgeService not initialized, returning empty list")
            return []
        
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
        if not self.initialized:
            logger.warning("⚠️ KnowledgeService not initialized, returning None")
            return None
        
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
        if not self.initialized:
            logger.warning("⚠️ KnowledgeService not initialized, cannot delete document")
            return False
        
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
