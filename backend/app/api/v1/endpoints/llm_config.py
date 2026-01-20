from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.llm_service import llm_service
from app.api.v1.endpoints.auth import get_current_user, get_superadmin_user

router = APIRouter()


class LLMConfigUpdate(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None


@router.get("/info")
async def get_llm_info(current_user: dict = Depends(get_current_user)):
    """
    Get LLM display information (for all users).
    Shows only the display name, no sensitive configuration.
    """
    return {
        "display_name": "CBIT CBIT-Elite",
        "description_zh": "您正在使用 CBIT 提供的高性能AI 服务。该模型由CBIT基于Qwen3 和VoxChina提供的语料微调训练，确保精准性能和稳定性。",
        "description_en": "You are using high-performance AI service provided by CBIT. The model is fine-tuned by CBIT based on Qwen3 and corpus provided by VoxChina, ensuring precision performance and stability.",
        "role": current_user["role"]
    }


@router.get("/config")
async def get_llm_config(current_user: dict = Depends(get_superadmin_user)):
    """
    Get current LLM configuration.
    Requires SUPERADMIN role.
    """
    try:
        from loguru import logger
        logger.info(f"[LLM Config] Getting config for user: {current_user.get('username', 'unknown')}")
        config = llm_service.get_current_config()
        logger.info(f"[LLM Config] Config retrieved successfully")
        return config
    except Exception as e:
        from loguru import logger
        logger.error(f"[LLM Config] Failed to get config: {e}")
        import traceback
        logger.error(f"[LLM Config] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_llm_config(
    config_update: LLMConfigUpdate,
    current_user: dict = Depends(get_superadmin_user)
):
    """
    Update LLM configuration.
    Requires SUPERADMIN role.
    """
    try:
        llm_service.update_config(
            provider=config_update.provider,
            model=config_update.model,
            api_key=config_update.api_key
        )
        return {
            "status": "success",
            "message": "LLM configuration updated",
            "config": llm_service.get_current_config()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models(current_user: dict = Depends(get_superadmin_user)):
    """
    Fetch available models from the configured LLM provider.
    Requires SUPERADMIN role.
    """
    try:
        models = await llm_service.fetch_available_models()
        return {
            "models": models,
            "provider": llm_service.provider,
            "display_name": "CBIT CBIT-Elite"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

