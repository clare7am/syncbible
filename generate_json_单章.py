"""
生成圣经分词 JSON（扁平结构）
输出：static/json/01_Gen_001.json
"""

import os
import json
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "bible.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "json")

BOOK_MAP = {
    1: "Gen", 2: "Ex", 3: "Lev", 4: "Num", 5: "Dt",
    6: "Jos", 7: "Jdg", 8: "Ru", 9: "1S", 10: "2S",
    11: "1K", 12: "2K", 13: "1Chr", 14: "2Chr",
    15: "Ezra", 16: "Ne", 17: "Tb", 18: "Jdt", 19: "Es",
    20: "1Mac", 21: "2Mac", 22: "Job", 23: "Ps", 24: "Pro",
    25: "Ecl", 26: "Song", 27: "Wis", 28: "Sir", 29: "Is",
    30: "Jer", 31: "Lm", 32: "Bar", 33: "Ezk", 34: "Dn",
    35: "Hos", 36: "Jl", 37: "Am", 38: "Ob", 39: "Jon",
    40: "Mic", 41: "Nh", 42: "Hb", 43: "Zep", 44: "Hg",
    45: "Zec", 46: "Mal", 47: "Mt", 48: "Mk", 49: "Lk",
    50: "Jn", 51: "Acts", 52: "Rom", 53: "1Cor", 54: "2Cor",
    55: "Gal", 56: "Eph", 57: "Phil", 58: "Col", 59: "1Thes",
    60: "2Thes", 61: "1Tim", 62: "2Tim", 63: "Tit", 64: "Phlm",
    65: "Heb", 66: "Jas", 67: "1P", 68: "2P", 69: "1Jn",
    70: "2Jn", 71: "3Jn", 72: "Jd", 73: "Rev"
}

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def generate_chapter_json(book_id, chapter):
    if book_id not in BOOK_MAP:
        raise ValueError(f"Unknown book_id: {book_id}")

    abbr = BOOK_MAP[book_id]

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT
            v.verse,
            v.text_cn,
            t.token AS word,
            t.type,
            t.entity_key,
            t.align_id,
            t.token_id,
            ts.start_time,
            ts.end_time
        FROM verses v
        LEFT JOIN tokens t
            ON v.book_id = t.book_id
           AND v.chapter = t.chapter
           AND v.verse = t.verse
        LEFT JOIN timestamps ts
            ON t.align_id = ts.id
        WHERE v.book_id = ?
          AND v.chapter = ?
        ORDER BY v.verse, t.token_id
    """, (book_id, chapter)).fetchall()

    verses = []
    current_verse = None
    verse_obj = None

    for r in rows:
        if current_verse != r["verse"]:
            verse_obj = {
                "verse": r["verse"],
                "text_cn": r["text_cn"],
                "words": []
            }
            verses.append(verse_obj)
            current_verse = r["verse"]

        if r["word"]:
            verse_obj["words"].append({
                "word": r["word"],
                "type": r["type"] or "",
                "entity_key": r["entity_key"] or "",
                "align_id": r["align_id"] or "",
                "start": r["start_time"] or 0,
                "end": r["end_time"] or 0
            })

    payload = {
        "has_tokens": any(len(v["words"]) > 0 for v in verses),
        "verses": verses
    }

    ensure_dir(OUTPUT_DIR)

    out_path = os.path.join(
        OUTPUT_DIR,
        f"{str(book_id).zfill(2)}_{abbr}_{str(chapter).zfill(3)}.json"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ {out_path}")
    conn.close()

if __name__ == "__main__":
    generate_chapter_json(1, 1)