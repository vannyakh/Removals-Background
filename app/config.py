"""
Application Configuration
Centralized configuration management
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Background Removal API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Model Configuration
    MODEL_TYPE: str = "u2net"  # "u2net" or "u2netp"
    MODEL_PATH: str = "models/u2net.pth"
    MODEL_P_PATH: str = "models/u2netp.pth"
    DEVICE: str = "auto"  # "auto", "cpu", "cuda"
    
    # Image Processing
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB (default)
    MAX_IMAGE_SIZE_REMOVEBG: int = 22 * 1024 * 1024  # 22MB for /removebg endpoint
    MAX_INPUT_MEGAPIXELS: int = 50  # Maximum input resolution in megapixels
    INPUT_SIZE: int = 320  # Model input size
    MAX_DIMENSION: int = 2048  # Max width/height for processing
    USE_MULTI_SCALE: bool = True  # Use multi-scale inference for better quality
    MASK_SMOOTHING: bool = True  # Apply mask smoothing
    EDGE_REFINEMENT: bool = True  # Apply edge refinement
    
    # Output Resolutions (in megapixels)
    OUTPUT_PREVIEW_MP: float = 0.25  # Preview resolution
    OUTPUT_FULL_MP: float = 25.0  # Full resolution
    OUTPUT_50MP_MP: float = 50.0  # 50MP resolution
    
    # Performance
    ENABLE_CACHE: bool = False  # Enable result caching
    CACHE_TTL: int = 3600  # Cache TTL in seconds
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    
    # Authentication
    API_KEY_ENABLED: bool = False  # Enable API key authentication
    API_KEY: Optional[str] = None  # API key for authentication
    OAUTH_ENABLED: bool = False  # Enable OAuth 2.0 authentication
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Convert model paths to Path objects and ensure directories exist
_model_path = Path(settings.MODEL_PATH)
_model_p_path = Path(settings.MODEL_P_PATH)
_model_path.parent.mkdir(parents=True, exist_ok=True)
_model_p_path.parent.mkdir(parents=True, exist_ok=True)

