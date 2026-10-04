from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    DATABASE_URL: str = 'postgresql://postgres:postgres@localhost:5432/ndvi_ai'
    SOURCE_DATA_DIR: str = 'D:/NDVI'
    PROCESSED_DATA_DIR: str = 'D:/NDVI/ndvi-ai-web/data/processed'
    CACHE_DIR: str = 'D:/NDVI/ndvi-ai-web/data/cache'
    BACKEND_PORT: int = 8000
    API_URL: str = 'http://localhost:8000'
    APP_DEBUG: bool = False
    CORS_ORIGINS: str = 'http://localhost:5173'

    @property
    def DEBUG(self) -> bool:
        return self.APP_DEBUG

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
