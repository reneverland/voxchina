from fastapi import APIRouter
from app.api.v1.endpoints import articles, vox_workshop, search, trending, voices, auth, llm_config, script_generation, academic_extract, knowledge, integrated_voiceover

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(trending.router, prefix="/trending", tags=["trending"])
api_router.include_router(voices.router, prefix="/voices", tags=["voices"])
api_router.include_router(llm_config.router, prefix="/llm", tags=["llm"])
api_router.include_router(academic_extract.router, prefix="/academic-extract", tags=["academic-extract"])
api_router.include_router(script_generation.router, prefix="/script", tags=["script-generation"])
api_router.include_router(vox_workshop.router, prefix="/vox", tags=["vox-workshop"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(integrated_voiceover.router, prefix="/integrated-voiceover", tags=["integrated-voiceover"])