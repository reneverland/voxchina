from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VoxChina AI Platform"
    API_V1_STR: str = "/api/v1"
    
    # Server Config
    HOST: str = "0.0.0.0"
    PORT: int = 8300
    
    # LLM Config
    LLM_PROVIDER: str = "openai"  # "openai" or "ollama"
    LLM_MODEL: str = "gpt-4o"  # Default model (upgraded to gpt-4o)
    
    # OpenAI Config
    OPENAI_API_KEY: str = ""  # Set via environment variable or .env file
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    
    # Ollama Config
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3-coder:30b" # Updated to available model
    OLLAMA_EMBEDDING_MODEL: str = "qwen3-embedding:latest" # Specific embedding model
    
    # Qdrant Config
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # Security Config
    SECRET_KEY: str = "your-secret-key-please-change-in-production" # Should be env var
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database Config
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./voxchina_email.db"
    
    # User Management - Format: {username: {"password": "xxx", "role": "admin/user"}}
    USERS: dict = {
        "admin": {
            "password": "goimba",
            "role": "superadmin",  # 超级管理员，可以配置所有 LLM
            "display_name": "Super Administrator"
        },
        "voxchina": {
            "password": "admin123",
            "role": "admin",  # 基本管理员，只能看到 CBIT LLM
            "display_name": "VoxChina Manager"
        },
        "voxadmin": {
            "password": "admin123",
            "role": "user",  # 普通用户，只能使用系统
            "display_name": "VoxChina Administrator"
        }
    }
    
    class Config:
        env_file = ".env"

settings = Settings()
