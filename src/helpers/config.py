from pydantic_settings import BaseSettings, SettingsConfigDict 
from typing import List

class settings(BaseSettings):
    APP_NAME:str
    APP_VERSION:str
    FILE_ALLOWED_TYPES:  list
    FILE_MAX_SIZE:int
    FILE_DEFAULT_CHUNK_SIZE :int
    MONGODB_URL:str
    MONGODB_DATABASE:str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None

    AZURE_OPENAI_API_KEY: str = None
    AZURE_OPENAI_API_VERSION: str = None
    AZURE_OPENAI_ENDPOINT: str = None

    GENERATION_MODEL_ID_LITERAL: List[str] = None
    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    INPUT_DAFAULT_MAX_CHARACTERS: int = None
    GENERATION_DAFAULT_MAX_TOKENS: int = None
    GENERATION_DAFAULT_TEMPERATURE: float = None

    class Config:
        env_file = ".env"


    # app_name: str = "RAG-App"
    # admin_email: str = "

def get_settings():
    # settings_instance = settings()
    # return settings_instance.
    return settings()