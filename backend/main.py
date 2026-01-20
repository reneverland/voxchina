from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import threading
from contextlib import asynccontextmanager
from loguru import logger
from app.core.config import settings
from app.api.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting background model loading...")
    # Lazy import to avoid blocking startup if TTS dependencies fail
    try:
        from app.services.tts_service import tts_service
        # Run load_models in a separate thread to avoid blocking startup
        thread = threading.Thread(target=tts_service.load_models)
        thread.start()
    except Exception as e:
        logger.warning(f"TTS service initialization skipped: {e}")
    yield
    # Shutdown: nothing specific yet

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

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

