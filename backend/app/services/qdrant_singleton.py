"""
Qdrant Client Singleton
单例模式的 Qdrant 客户端，避免本地存储并发访问问题
"""
from qdrant_client import QdrantClient
from loguru import logger
import os

class QdrantSingleton:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QdrantSingleton, cls).__new__(cls)
        return cls._instance
    
    def get_client(self):
        """获取 Qdrant 客户端实例"""
        if self._client is None:
            # 使用本地 Qdrant 存储
            qdrant_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "qdrant_data"
            )
            os.makedirs(qdrant_path, exist_ok=True)
            
            self._client = QdrantClient(path=qdrant_path)
            logger.info(f"✅ Qdrant singleton client initialized: {qdrant_path}")
        
        return self._client

# 全局单例实例
qdrant_singleton = QdrantSingleton()
