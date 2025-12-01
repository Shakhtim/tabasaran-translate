from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class TranslationDirection(str, Enum):
    TAB_TO_RUS = "tab-rus"
    RUS_TO_TAB = "rus-tab"


# Request models
class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    direction: TranslationDirection = TranslationDirection.TAB_TO_RUS
    use_llm: bool = True  # Whether to use LLM for context-aware translation


class LookupRequest(BaseModel):
    word: str = Field(..., min_length=1, max_length=100)
    fuzzy: bool = True  # Allow fuzzy matching


# Response models
class WordTranslation(BaseModel):
    word: str
    translations: List[str]
    part_of_speech: Optional[str] = None
    confidence: float = 1.0  # 1.0 = exact match, < 1.0 = fuzzy/inferred
    is_unknown: bool = False


class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    words: List[WordTranslation]
    direction: TranslationDirection
    llm_used: bool = False


class DictionaryEntry(BaseModel):
    id: int
    word: str
    word_normalized: Optional[str]
    root: Optional[str]
    part_of_speech: Optional[str]
    translations: List[str]
    examples: List[dict] = []
    is_verified: bool = False


class LookupResponse(BaseModel):
    query: str
    results: List[DictionaryEntry]
    total: int


class SuggestResponse(BaseModel):
    query: str
    suggestions: List[str]


# Health check
class HealthResponse(BaseModel):
    status: str
    database: bool
    vector_store: bool
    llm_server: bool
