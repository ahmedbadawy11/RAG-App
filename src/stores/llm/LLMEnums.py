from enum import Enum


class LLMEnums(Enum):

    OPENAI="OPENAI"
    AZURE_OPENAI="AZURE_OPENAI"
    COHERE="COHERE"


class OpenAIEnums(Enum):
    SYSTEM="system"
    USER="user"
    ASSISTANT="assistant"


class CoHereEnums(Enum):
    SYSTEM="system"
    USER="user"
    ASSISTANT="assistant"

    DOCUMENT="search_document"
    QUERY="search_query"

class DocumentTypesEnum(Enum):
    DOCUMENT="document"
    QUERY="query"