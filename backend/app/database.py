import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from app.config import settings


def init_db():
    """Initialize the database with required tables"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Words table (Tabasaran words)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                word_normalized TEXT,
                root TEXT,
                part_of_speech TEXT,
                is_verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Translations table (Russian translations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                translation TEXT NOT NULL,
                context TEXT,
                priority INTEGER DEFAULT 0,
                FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
            )
        """)

        # Examples table (usage examples)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                tabasaran_text TEXT,
                russian_text TEXT,
                source TEXT,
                FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
            )
        """)

        # Morphemes table (prefixes, suffixes, roots)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS morphemes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                morpheme TEXT NOT NULL,
                type TEXT CHECK(type IN ('prefix', 'suffix', 'root', 'infix')),
                meaning TEXT,
                examples TEXT
            )
        """)

        # Create indexes for fast search
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_word ON words(word)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_word_normalized ON words(word_normalized)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_root ON words(root)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_translation ON translations(translation)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_morpheme ON morphemes(morpheme)")

        conn.commit()


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Get database connection as context manager"""
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def normalize_word(word: str) -> str:
    """Normalize word for search (lowercase, remove accents)"""
    # Remove common diacritics and normalize
    word = word.lower().strip()
    # Add more normalization rules as needed for Tabasaran
    return word
