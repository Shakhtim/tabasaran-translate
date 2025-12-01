"""
Main translation engine.
Combines dictionary lookup, morphological analysis, and LLM for translation.
"""

import re
from typing import List, Tuple

from app.models import (
    TranslateRequest, TranslateResponse, WordTranslation,
    TranslationDirection
)
from app.services.dictionary import dictionary_service
from app.services.morphology import morphology_service
from app.services.llm_client import llm_client


class TranslatorService:
    """Main translation service"""

    def __init__(self):
        self.dictionary = dictionary_service
        self.morphology = morphology_service
        self.llm = llm_client

    async def translate(self, request: TranslateRequest) -> TranslateResponse:
        """
        Translate text using hybrid approach:
        1. Tokenize text
        2. Look up each word in dictionary
        3. Use morphology for unknown words
        4. Optionally use LLM for context-aware translation
        """
        text = request.text.strip()
        direction = request.direction

        # Tokenize
        tokens = self._tokenize(text)

        # Translate each token
        word_translations = []
        context_entries = []

        for token in tokens:
            if self._is_punctuation(token):
                # Keep punctuation as-is
                word_translations.append(WordTranslation(
                    word=token,
                    translations=[token],
                    confidence=1.0
                ))
            else:
                # Translate word
                wt = await self._translate_word(token, direction)
                word_translations.append(wt)

                # Collect context for LLM
                if not wt.is_unknown and wt.translations:
                    context_entries.append({
                        "word": wt.word,
                        "translations": wt.translations
                    })

        # Try LLM for better translation
        llm_used = False
        if request.use_llm and context_entries:
            llm_translation = await self.llm.translate(
                text=text,
                context=context_entries,
                direction=direction.value
            )
            if llm_translation:
                llm_used = True
                translated_text = llm_translation
            else:
                # Fallback to word-by-word
                translated_text = self._assemble_translation(word_translations)
        else:
            translated_text = self._assemble_translation(word_translations)

        return TranslateResponse(
            original_text=text,
            translated_text=translated_text,
            words=word_translations,
            direction=direction,
            llm_used=llm_used
        )

    async def _translate_word(
        self,
        word: str,
        direction: TranslationDirection
    ) -> WordTranslation:
        """Translate a single word"""

        if direction == TranslationDirection.TAB_TO_RUS:
            return await self._translate_tab_to_rus(word)
        else:
            return await self._translate_rus_to_tab(word)

    async def _translate_tab_to_rus(self, word: str) -> WordTranslation:
        """Translate Tabasaran word to Russian"""

        # 1. Try exact match
        entries = self.dictionary.lookup_exact(word)
        if entries:
            entry = entries[0]
            return WordTranslation(
                word=word,
                translations=entry.translations,
                part_of_speech=entry.part_of_speech,
                confidence=1.0
            )

        # 2. Try morphological analysis
        analysis = self.morphology.analyze(word)
        for possible_root in analysis.possible_roots:
            if possible_root != word.lower():
                entries = self.dictionary.lookup_exact(possible_root)
                if entries:
                    entry = entries[0]
                    return WordTranslation(
                        word=word,
                        translations=entry.translations,
                        part_of_speech=entry.part_of_speech,
                        confidence=0.8  # Lower confidence for morphological match
                    )

        # 3. Try fuzzy match
        fuzzy_results = self.dictionary.lookup_fuzzy(word)
        if fuzzy_results:
            entry, distance = fuzzy_results[0]
            confidence = max(0.3, 1.0 - (distance * 0.2))
            return WordTranslation(
                word=word,
                translations=entry.translations,
                part_of_speech=entry.part_of_speech,
                confidence=confidence
            )

        # 4. Unknown word
        return WordTranslation(
            word=word,
            translations=[word],  # Keep original
            confidence=0.0,
            is_unknown=True
        )

    async def _translate_rus_to_tab(self, word: str) -> WordTranslation:
        """Translate Russian word to Tabasaran"""

        entries = self.dictionary.search_russian(word)
        if entries:
            # Return Tabasaran words that have this Russian translation
            tabasaran_words = [e.word for e in entries[:3]]
            return WordTranslation(
                word=word,
                translations=tabasaran_words,
                confidence=0.9
            )

        return WordTranslation(
            word=word,
            translations=[word],
            confidence=0.0,
            is_unknown=True
        )

    def _tokenize(self, text: str) -> List[str]:
        """Split text into tokens (words and punctuation)"""
        # Split on word boundaries, keeping punctuation
        pattern = r'(\s+|[.,!?;:"\'\(\)\[\]{}])'
        tokens = re.split(pattern, text)
        return [t for t in tokens if t and not t.isspace()]

    def _is_punctuation(self, token: str) -> bool:
        """Check if token is punctuation"""
        return bool(re.match(r'^[.,!?;:"\'\(\)\[\]{}]+$', token))

    def _assemble_translation(self, word_translations: List[WordTranslation]) -> str:
        """Assemble translated words into text"""
        parts = []
        for wt in word_translations:
            if wt.translations:
                parts.append(wt.translations[0])
            else:
                parts.append(wt.word)

        # Simple assembly - join with spaces, fix punctuation spacing
        text = " ".join(parts)
        # Remove spaces before punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        return text


# Singleton instance
translator_service = TranslatorService()
