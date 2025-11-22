from enum import Enum


class LLMEnums(Enum):

    OPENAI="OPENAI"
    AZURE_OPENAI="AZURE_OPENAI"
    COHERE="COHERE"


class OpenAIEnums(Enum):
    SYSTEM="system"
    USER="user"
    ASSISTANT="assistant"