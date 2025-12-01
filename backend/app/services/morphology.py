"""
Morphological analyzer for Tabasaran language.

Tabasaran is an agglutinative language with complex morphology.
Key features:
- SOV word order
- Rich case system (many local cases)
- Verb agreement with subject
- Prefixes and suffixes

This module provides basic morphological analysis for translation.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MorphemeInfo:
    """Information about a morpheme"""
    morpheme: str
    type: str  # prefix, suffix, root, infix
    meaning: Optional[str] = None


@dataclass
class MorphAnalysis:
    """Result of morphological analysis"""
    original: str
    root: Optional[str]
    prefix: List[MorphemeInfo]
    suffix: List[MorphemeInfo]
    possible_roots: List[str]


# Common Tabasaran suffixes (to be expanded based on dictionary analysis)
# Based on rosettaproject_tab_phon-1.pdf phonetics info
COMMON_SUFFIXES = [
    # Noun case suffixes
    ("ди", "genitive", "родительный падеж"),
    ("з", "dative", "дательный падеж"),
    ("ъ", "ergative", "эргативный падеж"),
    ("ин", "locative", "местный падеж"),

    # Plural
    ("ар", "plural", "множественное число"),
    ("ер", "plural", "множественное число"),

    # Verb suffixes
    ("уз", "1st person plural", "1 лицо мн.ч."),
    ("ру", "infinitive", "инфинитив"),

    # Adjective suffixes
    ("ан", "adjective", "прилагательное"),
]

COMMON_PREFIXES = [
    # Negation
    ("дар", "negation", "отрицание"),
]


class MorphologyService:
    """Service for morphological analysis of Tabasaran words"""

    def __init__(self):
        self.suffixes = COMMON_SUFFIXES
        self.prefixes = COMMON_PREFIXES

    def analyze(self, word: str) -> MorphAnalysis:
        """Analyze morphological structure of a word"""
        original = word
        word_lower = word.lower()

        found_prefixes = []
        found_suffixes = []
        possible_roots = []

        # Try to find prefixes
        remaining = word_lower
        for prefix, ptype, meaning in self.prefixes:
            if remaining.startswith(prefix):
                found_prefixes.append(MorphemeInfo(prefix, "prefix", meaning))
                remaining = remaining[len(prefix):]
                break

        # Try to find suffixes (from the end)
        for suffix, stype, meaning in sorted(self.suffixes, key=lambda x: -len(x[0])):
            if remaining.endswith(suffix) and len(remaining) > len(suffix):
                found_suffixes.insert(0, MorphemeInfo(suffix, "suffix", meaning))
                remaining = remaining[:-len(suffix)]

        # What remains is likely the root
        if remaining:
            possible_roots.append(remaining)

        # Also try the original word as a possible root
        if word_lower not in possible_roots:
            possible_roots.append(word_lower)

        return MorphAnalysis(
            original=original,
            root=remaining if remaining else None,
            prefix=found_prefixes,
            suffix=found_suffixes,
            possible_roots=possible_roots
        )

    def get_possible_forms(self, root: str) -> List[str]:
        """Generate possible word forms from a root"""
        forms = [root]

        # Add common suffix variations
        for suffix, _, _ in self.suffixes[:5]:  # Limit to common ones
            forms.append(root + suffix)

        return forms

    def strip_affixes(self, word: str) -> List[str]:
        """Return list of possible roots by stripping affixes"""
        analysis = self.analyze(word)
        return analysis.possible_roots


# Singleton instance
morphology_service = MorphologyService()
