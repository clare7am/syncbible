#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
from typing import List, Tuple

DB_PATH = "db/bible.db"


def get_book_abbr(cursor, book_id: int) -> str:
    cursor.execute("SELECT abbr_en FROM book WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"book_id={book_id} 在 book 表中不存在")
    return row[0]


def segment_english_preserve(text: str) -> List[Tuple[str, str]]:
    if not text:
        return []

    tokens = []
    current = ""
    current_type = None

    def flush():
        nonlocal current, current_type
        if current:
            tokens.append((current, current_type))
            current = ""
            current_type = None

    for ch in text:
        if ch.isalpha():
            t = "word"
        elif ch.isdigit():
            t = "number"
        elif ch.isspace():
            t = "space"
        else:
            t = "punct"

        if t != current_type:
            flush()
            current_type = t

        current += ch

    flush()
    return tokens


def build_tokens_for_chapter(book_abbr: str, book_id: int, chapter: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"📖 处理章节：{book_abbr} {chapter}")

    cursor.execute("""
        SELECT v.id, v.verse, v.text_en
        FROM verses v
        WHERE v.book_id = ?
          AND v.chapter = ?
          AND v.text_en IS NOT NULL
        ORDER BY v.verse
    """, (book_id, chapter))

    verses = cursor.fetchall()
    print(f"  需要处理的 verse 数：{len(verses)}")

    token_rows = []

    for verse_id, verse_num, text_en in verses:
        tokens = segment_english_preserve(text_en)

        reconstructed = "".join(t for t, _ in tokens)
        if reconstructed != text_en:
            print("❌ 拼接不一致")
            print("verse:", verse_id)
            print("原句:", repr(text_en))
            print("拼接:", repr(reconstructed))
            continue

        for idx, (token, token_type) in enumerate(tokens, start=1):
            token_id = f"{book_abbr}.{chapter}.{verse_num}.{idx}"
            token_rows.append((
                token_id,
                book_id,
                chapter,
                verse_num,
                idx,
                token,
                token_type,
                None
            ))

    cursor.executemany("""
        INSERT INTO tokens (
            id, book_id, chapter, verse,
            token_id, token, type, entity_key
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, token_rows)

    print(f"✅ 插入 token 数：{len(token_rows)}")

    cursor.execute("""
        SELECT id
        FROM tokens
        WHERE book_id = ?
          AND chapter = ?
          AND type = 'word'
        ORDER BY chapter, verse, token_id
    """, (book_id, chapter))

    word_tokens = cursor.fetchall()

    for seq, (token_id,) in enumerate(word_tokens, start=1):
        align_id = f"{book_id:02d}_{book_abbr}_{chapter:03d}__{seq:04d}"
        cursor.execute("""
            UPDATE tokens
            SET word_seq = ?, align_id = ?
            WHERE id = ?
        """, (seq, align_id, token_id))

    print(f"✅ 已填充 word_seq / align_id 数量：{len(word_tokens)}")

    conn.commit()
    conn.close()
    print("🎉 本章 token 构建完成")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：python generate_tokens_for_chapter.py <book_id> <chapter>")
        print("示例：python generate_tokens_for_chapter.py 1 6")
        sys.exit(1)

    book_id = int(sys.argv[1])
    chapter = int(sys.argv[2])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    book_abbr = get_book_abbr(cursor, book_id)
    conn.close()

    build_tokens_for_chapter(book_abbr, book_id, chapter)