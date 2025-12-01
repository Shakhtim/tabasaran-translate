from fastapi import APIRouter, HTTPException

from app.models import TranslateRequest, TranslateResponse
from app.services.translator import translator_service


router = APIRouter(prefix="/translate", tags=["Translation"])


@router.post("", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """
    Translate text between Tabasaran and Russian.

    - **text**: Text to translate (max 5000 characters)
    - **direction**: Translation direction (tab-rus or rus-tab)
    - **use_llm**: Whether to use LLM for context-aware translation
    """
    try:
        result = await translator_service.translate(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
