"""
LLM client for GPU server communication.
Supports Ollama API format.
"""

import httpx
from typing import Optional, List
import json

from app.config import settings


class LLMClient:
    """Client for communicating with LLM server"""

    def __init__(self):
        self.base_url = settings.LLM_SERVER_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT

    async def translate(
        self,
        text: str,
        context: List[dict],
        direction: str = "tab-rus"
    ) -> Optional[str]:
        """
        Translate text using LLM with dictionary context.

        Args:
            text: Text to translate
            context: List of dictionary entries for context
            direction: Translation direction (tab-rus or rus-tab)

        Returns:
            Translated text or None if failed
        """
        # Format context from dictionary
        context_text = self._format_context(context)

        if direction == "tab-rus":
            prompt = f"""Ты - эксперт-переводчик табасаранского языка на русский.

ГРАММАТИКА ТАБАСАРАНСКОГО ЯЗЫКА:
- Агглютинативный язык (суффиксы добавляются к корню)
- Эргативный строй (субъект переходного глагола в эргативе)
- 46 падежей (локативные серии)
- Порядок слов: SOV (подлежащее-дополнение-сказуемое)
- Глагол согласуется с субъектом по классу и числу

ЧАСТЫЕ СУФФИКСЫ:
- -ар/-ер — множественное число
- -ин — родительный падеж
- -из — дательный падеж
- -на — эргативный падеж
- -хъ — локатив (внутри)
- -ъ — локатив (на поверхности)

СЛОВАРНЫЙ КОНТЕКСТ:
{context_text}

ПРИМЕРЫ ПЕРЕВОДОВ:
• "Узу школайиз шулу" → "Я иду в школу"
• "Баба аьхю" → "Мать большая"
• "Дада гъафну" → "Отец пришёл"

Переведи на русский язык, сохраняя смысл:
"{text}"

Ответь ТОЛЬКО переводом, без пояснений."""
        else:
            prompt = f"""Ты - эксперт-переводчик русского языка на табасаранский.

ГРАММАТИКА ТАБАСАРАНСКОГО ЯЗЫКА:
- Агглютинативный язык (суффиксы добавляются к корню)
- Порядок слов: SOV (подлежащее-дополнение-сказуемое)
- Глагол ставится в конце предложения

СЛОВАРНЫЙ КОНТЕКСТ:
{context_text}

ПРИМЕРЫ ПЕРЕВОДОВ:
• "Я иду в школу" → "Узу школайиз шулу"
• "Мать большая" → "Баба аьхю"
• "Отец пришёл" → "Дада гъафну"

Переведи на табасаранский язык:
"{text}"

Ответь ТОЛЬКО переводом, без пояснений."""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "top_p": 0.9,
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()

        except httpx.TimeoutException:
            print(f"LLM request timeout")
        except httpx.ConnectError:
            print(f"Cannot connect to LLM server at {self.base_url}")
        except Exception as e:
            print(f"LLM request error: {e}")

        return None

    async def is_available(self) -> bool:
        """Check if LLM server is available"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False

    def _format_context(self, context: List[dict]) -> str:
        """Format dictionary entries as context for LLM"""
        if not context:
            return "Контекст из словаря отсутствует."

        lines = []
        for entry in context[:10]:  # Limit context size
            word = entry.get("word", "")
            translations = entry.get("translations", [])
            if translations:
                trans_str = ", ".join(translations[:3])
                lines.append(f"• {word} — {trans_str}")

        return "\n".join(lines) if lines else "Контекст из словаря отсутствует."


# Singleton instance
llm_client = LLMClient()
