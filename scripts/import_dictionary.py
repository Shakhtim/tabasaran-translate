"""
Import extracted dictionary into SQLite database.
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import init_db, get_db, normalize_word
from app.config import settings


DATA_DIR = Path(__file__).parent.parent / "backend" / "data"


def import_from_json(json_path: Path):
    """Import dictionary entries from JSON file"""
    print(f"Importing from {json_path}...")

    with open(json_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    print(f"Found {len(entries)} entries")

    # Initialize database
    init_db()

    imported = 0
    skipped = 0

    with get_db() as conn:
        cursor = conn.cursor()

        for entry in entries:
            word = entry.get('word', '').strip()
            translations = entry.get('translations', [])

            if not word or not translations:
                skipped += 1
                continue

            # Check if word already exists
            cursor.execute("SELECT id FROM words WHERE word = ?", (word,))
            existing = cursor.fetchone()

            if existing:
                word_id = existing['id']
            else:
                # Insert new word
                cursor.execute("""
                    INSERT INTO words (word, word_normalized)
                    VALUES (?, ?)
                """, (word, normalize_word(word)))
                word_id = cursor.lastrowid

            # Insert translations
            for i, translation in enumerate(translations):
                translation = translation.strip()
                if translation:
                    # Check if translation exists
                    cursor.execute("""
                        SELECT id FROM translations
                        WHERE word_id = ? AND translation = ?
                    """, (word_id, translation))

                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO translations (word_id, translation, priority)
                            VALUES (?, ?, ?)
                        """, (word_id, translation, len(translations) - i))

            imported += 1

            if imported % 1000 == 0:
                print(f"  Imported {imported} entries...")
                conn.commit()

        conn.commit()

    print(f"Import complete!")
    print(f"  Imported: {imported}")
    print(f"  Skipped: {skipped}")


def import_sample_data():
    """Import sample data for testing"""
    print("Importing sample data...")

    init_db()

    sample_entries = [
        {"word": "аба", "translations": ["отец", "папа"]},
        {"word": "баба", "translations": ["мать", "мама"]},
        {"word": "бай", "translations": ["дом"]},
        {"word": "йиз", "translations": ["вода"]},
        {"word": "гаф", "translations": ["слово", "речь"]},
        {"word": "китаб", "translations": ["книга"]},
        {"word": "дерс", "translations": ["урок"]},
        {"word": "муаллим", "translations": ["учитель"]},
        {"word": "шагьур", "translations": ["город"]},
        {"word": "хъул", "translations": ["село", "деревня"]},
        {"word": "хал", "translations": ["комната"]},
        {"word": "гъил", "translations": ["рука"]},
        {"word": "кьил", "translations": ["голова"]},
        {"word": "уьл", "translations": ["сердце"]},
        {"word": "йикь", "translations": ["день"]},
        {"word": "йишв", "translations": ["ночь"]},
        {"word": "ат", "translations": ["лошадь"]},
        {"word": "бецI", "translations": ["волк"]},
        {"word": "лик", "translations": ["собака"]},
        {"word": "кату", "translations": ["кошка"]},
    ]

    with get_db() as conn:
        cursor = conn.cursor()

        for entry in sample_entries:
            word = entry['word']
            translations = entry['translations']

            cursor.execute("""
                INSERT OR IGNORE INTO words (word, word_normalized)
                VALUES (?, ?)
            """, (word, normalize_word(word)))

            cursor.execute("SELECT id FROM words WHERE word = ?", (word,))
            word_id = cursor.fetchone()['id']

            for i, translation in enumerate(translations):
                cursor.execute("""
                    INSERT OR IGNORE INTO translations (word_id, translation, priority)
                    VALUES (?, ?, ?)
                """, (word_id, translation, len(translations) - i))

        conn.commit()

    print(f"Imported {len(sample_entries)} sample entries")


def show_stats():
    """Show database statistics"""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as cnt FROM words")
        words_count = cursor.fetchone()['cnt']

        cursor.execute("SELECT COUNT(*) as cnt FROM translations")
        trans_count = cursor.fetchone()['cnt']

        cursor.execute("SELECT COUNT(*) as cnt FROM examples")
        examples_count = cursor.fetchone()['cnt']

        print(f"\nDatabase Statistics:")
        print(f"  Words: {words_count}")
        print(f"  Translations: {trans_count}")
        print(f"  Examples: {examples_count}")
        print(f"  Database: {settings.DATABASE_PATH}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import dictionary into database")
    parser.add_argument("--json", type=str, help="JSON file to import")
    parser.add_argument("--sample", action="store_true", help="Import sample data for testing")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")

    args = parser.parse_args()

    if args.json:
        import_from_json(Path(args.json))
        show_stats()
    elif args.sample:
        import_sample_data()
        show_stats()
    elif args.stats:
        show_stats()
    else:
        print("Usage:")
        print("  python import_dictionary.py --json dictionary_raw.json")
        print("  python import_dictionary.py --sample")
        print("  python import_dictionary.py --stats")
