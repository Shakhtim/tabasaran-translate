from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models import LookupResponse, SuggestResponse, DictionaryEntry
from app.services.dictionary import dictionary_service


router = APIRouter(prefix="/dictionary", tags=["Dictionary"])


@router.get("/lookup/{word}", response_model=LookupResponse)
async def lookup_word(
    word: str,
    fuzzy: bool = Query(True, description="Allow fuzzy matching")
):
    """
    Look up a word in the dictionary.

    - **word**: Word to look up
    - **fuzzy**: If true, include fuzzy matches when exact match not found
    """
    # Try exact match first
    results = dictionary_service.lookup_exact(word)

    # If no exact match and fuzzy enabled, try fuzzy
    if not results and fuzzy:
        fuzzy_results = dictionary_service.lookup_fuzzy(word)
        results = [entry for entry, distance in fuzzy_results]

    return LookupResponse(
        query=word,
        results=results,
        total=len(results)
    )


@router.get("/suggest", response_model=SuggestResponse)
async def suggest_words(
    q: str = Query(..., min_length=1, description="Query prefix"),
    limit: int = Query(10, ge=1, le=50, description="Max suggestions")
):
    """
    Get word suggestions for autocomplete.

    - **q**: Query prefix
    - **limit**: Maximum number of suggestions
    """
    suggestions = dictionary_service.suggest(q, limit)

    return SuggestResponse(
        query=q,
        suggestions=suggestions
    )


@router.get("/word/{word_id}", response_model=DictionaryEntry)
async def get_word(word_id: int):
    """
    Get detailed information about a word by ID.

    - **word_id**: Word ID in database
    """
    entry = dictionary_service.get_by_id(word_id)

    if not entry:
        raise HTTPException(status_code=404, detail="Word not found")

    return entry


@router.get("/search/russian", response_model=LookupResponse)
async def search_by_russian(
    word: str = Query(..., min_length=1, description="Russian word to search")
):
    """
    Search dictionary by Russian translation (for reverse translation).

    - **word**: Russian word to find Tabasaran equivalents for
    """
    results = dictionary_service.search_russian(word)

    return LookupResponse(
        query=word,
        results=results,
        total=len(results)
    )
