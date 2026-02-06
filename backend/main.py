#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VoxChina Backend - Main Application
作者：Ren CBIT https://github.com/reneverland/
"""

# ============================================================================
# 重要：必须在所有导入之前设置环境变量！
# 解决 www 用户 home 目录权限问题
# ============================================================================
import os
import sys

# 设置缓存目录到 backend 目录
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# 设置所有可能的缓存环境变量
os.environ["XDG_CACHE_HOME"] = CACHE_DIR
os.environ["HF_HOME"] = os.path.join(CACHE_DIR, "huggingface")
os.environ["TRANSFORMERS_CACHE"] = os.path.join(CACHE_DIR, "transformers")
os.environ["HF_DATASETS_CACHE"] = os.path.join(CACHE_DIR, "datasets")
os.environ["TORCH_HOME"] = os.path.join(CACHE_DIR, "torch")

# 创建所有子目录
for subdir in ["huggingface", "transformers", "datasets", "torch"]:
    os.makedirs(os.path.join(CACHE_DIR, subdir), exist_ok=True)

print(f"[Cache Init] 📁 Cache directory: {CACHE_DIR}")
print(f"[Cache Init] 📁 HF_HOME: {os.environ['HF_HOME']}")
print(f"[Cache Init] 📁 TRANSFORMERS_CACHE: {os.environ['TRANSFORMERS_CACHE']}")

# ============================================================================
# 现在才导入其他模块
# ============================================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uvicorn
import threading
from contextlib import asynccontextmanager
from loguru import logger
from app.core.config import settings
from app.api.api import api_router

logger.info(f"✅ Cache directory successfully set to: {CACHE_DIR}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting VoxChina backend services...")
    
    # 1. 初始化核心服务（知识库、LLM等）
    logger.info("📦 Initializing core services...")
    
    # 初始化数据库
    try:
        from app.db.init_db import init_db
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")

    try:
        from app.services.knowledge_service import knowledge_service
        if knowledge_service.initialized:
            logger.info("✅ KnowledgeService initialized successfully")
        else:
            logger.warning("⚠️ KnowledgeService initialization failed, running in degraded mode")
    except Exception as e:
        logger.error(f"❌ Failed to import KnowledgeService: {e}")
    
    try:
        from app.services.llm_service import llm_service
        logger.info("✅ LLMService initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import LLMService: {e}")
    
    try:
        from app.services.voice_service import voice_service
        logger.info("✅ VoiceService initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import VoiceService: {e}")
    
    # 2. 初始化 TTS 模型（在后台线程中）
    logger.info("🎤 Starting background TTS model loading...")
    try:
        from app.services.tts_service import tts_service
        # Run load_models in a separate thread to avoid blocking startup
        thread = threading.Thread(target=tts_service.load_models)
        thread.start()
        logger.info("✅ TTS model loading started in background")
    except Exception as e:
        logger.warning(f"⚠️ TTS service initialization skipped: {e}")
    
    logger.info("✅ All services initialized, backend ready!")
    
    yield
    
    # Shutdown: nothing specific yet
    logger.info("🛑 Shutting down VoxChina backend...")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# UTF-8 Encoding Middleware - Ensure all JSON responses use UTF-8
class UTF8Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Ensure JSON responses explicitly set UTF-8 charset
        if response.headers.get("content-type", "").startswith("application/json"):
            response.headers["content-type"] = "application/json; charset=utf-8"
        return response

app.add_middleware(UTF8Middleware)

# CORS Setup - Must be added before mounting static files
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8400",
        "http://localhost:5173",
        "http://127.0.0.1:8400",
        "http://127.0.0.1:5173",
        "http://llmhi.com",
        "http://llmhi.com:8400",
        "http://llmhi.com:8300",
        "http://llmhi.com:8301",
        "https://llmhi.com",
        "https://llmhi.com:8400",
        "https://llmhi.com:8300",
        "https://llmhi.com:8301",
        "http://113.106.62.42:8400",
        "http://113.106.62.42:8300",
        "https://113.106.62.42:8400",
        "https://113.106.62.42:8300"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose headers for better CORS support
)

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "VoxChina AI Platform API is running", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)

