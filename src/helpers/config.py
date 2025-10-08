from pydantic_settings import BaseSettings, SettingsConfigDict 


class settings(BaseSettings):
    APP_NAME:str
    APP_VERSION:str
    FILE_ALLOWED_TYPES:  list
    FILE_MAX_SIZE:int
    FILE_DEFAULT_CHUNK_SIZE :int

    class Config:
        env_file = ".env"


    # app_name: str = "RAG-App"
    # admin_email: str = "

def get_settings():
    # settings_instance = settings()
    # return settings_instance.
    return settings()