import sqlite3
from typing import List, Optional, Tuple
import Levenshtein

from app.database import get_db, normalize_word
from app.models import DictionaryEntry
from app.config import settings


class DictionaryService:
    """Service for dictionary lookups"""

    def lookup_exact(self, word: str) -> List[DictionaryEntry]:
        """Find exact match for a word"""
        normalized = normalize_word(word)

        with get_db() as conn:
            cursor = conn.cursor()

            # Try exact match first
            cursor.execute("""
                SELECT w.id, w.word, w.word_normalized, w.root, w.part_of_speech, w.is_verified
                FROM words w
                WHERE w.word = ? OR w.word_normalized = ?
            """, (word, normalized))

            rows = cursor.fetchall()
            return [self._row_to_entry(conn, row) for row in rows]

    def lookup_fuzzy(self, word: str, max_distance: int = None) -> List[Tuple[DictionaryEntry, int]]:
        """Find fuzzy matches using Levenshtein distance"""
        if max_distance is None:
            max_distance = settings.FUZZY_THRESHOLD

        normalized = normalize_word(word)
        results = []

        with get_db() as conn:
            cursor = conn.cursor()

            # Get all words (for small dictionaries this is fine)
            # For large dictionaries, use prefix filtering
            cursor.execute("""
                SELECT w.id, w.word, w.word_normalized, w.root, w.part_of_speech, w.is_verified
                FROM words w
            """)

            for row in cursor.fetchall():
                db_word = row['word_normalized'] or row['word']
                distance = Levenshtein.distance(normalized, db_word.lower())

                if distance <= max_distance and distance > 0:
                    entry = self._row_to_entry(conn, row)
                    results.append((entry, distance))

        # Sort by distance
        results.sort(key=lambda x: x[1])
        return results[:10]  # Limit to 10 results

    def lookup_by_root(self, root: str) -> List[DictionaryEntry]:
        """Find words by root"""
        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT w.id, w.word, w.word_normalized, w.root, w.part_of_speech, w.is_verified
                FROM words w
                WHERE w.root = ?
            """, (root,))

            rows = cursor.fetchall()
            return [self._row_to_entry(conn, row) for row in rows]

    def suggest(self, prefix: str, limit: int = 10) -> List[str]:
        """Get word suggestions for autocomplete"""
        normalized = normalize_word(prefix)

        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT word
                FROM words
                WHERE word_normalized LIKE ? OR word LIKE ?
                ORDER BY word
                LIMIT ?
            """, (f"{normalized}%", f"{prefix}%", limit))

            return [row['word'] for row in cursor.fetchall()]

    def get_by_id(self, word_id: int) -> Optional[DictionaryEntry]:
        """Get word by ID"""
        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT w.id, w.word, w.word_normalized, w.root, w.part_of_speech, w.is_verified
                FROM words w
                WHERE w.id = ?
            """, (word_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_entry(conn, row)
            return None

    def search_russian(self, russian_word: str) -> List[DictionaryEntry]:
        """Search by Russian translation (for reverse translation)"""
        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT w.id, w.word, w.word_normalized, w.root, w.part_of_speech, w.is_verified
                FROM words w
                JOIN translations t ON w.id = t.word_id
                WHERE t.translation LIKE ?
                ORDER BY t.priority DESC
            """, (f"%{russian_word}%",))

            rows = cursor.fetchall()
            return [self._row_to_entry(conn, row) for row in rows]

    def _row_to_entry(self, conn: sqlite3.Connection, row: sqlite3.Row) -> DictionaryEntry:
        """Convert database row to DictionaryEntry"""
        cursor = conn.cursor()

        # Get translations
        cursor.execute("""
            SELECT translation FROM translations
            WHERE word_id = ?
            ORDER BY priority DESC
        """, (row['id'],))
        translations = [r['translation'] for r in cursor.fetchall()]

        # Get examples
        cursor.execute("""
            SELECT tabasaran_text, russian_text, source FROM examples
            WHERE word_id = ?
        """, (row['id'],))
        examples = [
            {"tabasaran": r['tabasaran_text'], "russian": r['russian_text'], "source": r['source']}
            for r in cursor.fetchall()
        ]

        return DictionaryEntry(
            id=row['id'],
            word=row['word'],
            word_normalized=row['word_normalized'],
            root=row['root'],
            part_of_speech=row['part_of_speech'],
            translations=translations,
            examples=examples,
            is_verified=bool(row['is_verified'])
        )


# Singleton instance
dictionary_service = DictionaryService()
