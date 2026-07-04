#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_chapter_json.py
生成指定章节的分词 JSON
用法：python generate_chapter_json.py <book_id> <chapter>
"""

import os
import json
import sqlite3
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "bible.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "json")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def get_book_abbr(book_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT abbr_en FROM book WHERE id = ?", (book_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise ValueError(f"book_id={book_id} 不存在")
    return row[0]


def generate_chapter_json(book_id: int, chapter: int):
    abbr = get_book_abbr(book_id)

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
    if len(sys.argv) != 3:
        print("用法：python generate_chapter_json.py <book_id> <chapter>")
        print("示例：python generate_chapter_json.py 1 6")
        sys.exit(1)

    book_id = int(sys.argv[1])
    chapter = int(sys.argv[2])

    generate_chapter_json(book_id, chapter)