#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
w_00_highlight_for_book.py
多卷书工作流：从 book_start 到 book_end
用法：
    python w_00_highlight_for_book.py <book_start> <book_end>
"""

import sys
import subprocess
import sqlite3
import os
import traceback
import time

DB_PATH = "db/bible.db"
OUTPUT_JSON_DIR = "static/json"
CHAPTER_SCRIPT = "w_00_highlight_for_chapter.py"


def get_book_info(book_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT abbr_en, max_chapter FROM book WHERE id = ?",
        (book_id,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"book_id={book_id} 不存在")
    return row[0], row[1]


def build_json_path(book_id: int, abbr: str, chapter: int) -> str:
    filename = f"{str(book_id).zfill(2)}_{abbr}_{str(chapter).zfill(3)}.json"
    return os.path.join(OUTPUT_JSON_DIR, filename)


def run_chapter(book_id: int, abbr: str, chapter: int):
    json_path = build_json_path(book_id, abbr, chapter)

    if os.path.exists(json_path):
        print(f"⏭️  已存在，跳过：{abbr} {chapter}")
        return "skipped", None

    print(f"\n▶ 开始处理：{abbr} {chapter}")
    start = time.time()

    result = subprocess.run(
        ["python", CHAPTER_SCRIPT, str(book_id), str(chapter)],
        capture_output=True,
        text=True
    )

    elapsed = time.time() - start

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print(f"❌ 失败：{abbr} {chapter}（{elapsed:.2f}s）")
        return "failed", result.stderr

    print(f"✅ 完成：{abbr} {chapter}（{elapsed:.2f}s）")
    return "ok", None


def run_book(book_id: int, stats: dict, problems: list):
    abbr, max_chapter = get_book_info(book_id)
    print(f"\n{'='*60}")
    print(f"📖 开始卷书：{abbr}（共 {max_chapter} 章）")
    print(f"{'='*60}")

    t0 = time.time()

    for chapter in range(1, max_chapter + 1):
        try:
            status, detail = run_chapter(book_id, abbr, chapter)
            stats[status] += 1
            if status == "failed":
                problems.append({
                    "book_id": book_id,
                    "abbr": abbr,
                    "chapter": chapter,
                    "detail": detail
                })
        except Exception:
            stats["failed"] += 1
            problems.append({
                "book_id": book_id,
                "abbr": abbr,
                "chapter": chapter,
                "detail": traceback.format_exc()
            })

    total = time.time() - t0
    print(f"\n📖 {abbr} 完成："
          f"✅{stats['ok']} ⏭️{stats['skipped']} ❌{stats['failed']} "
          f"⏱ {total:.2f}s")


def main(book_start: int, book_end: int):
    stats = {"ok": 0, "skipped": 0, "failed": 0}
    problems = []

    t0 = time.time()

    for book_id in range(book_start, book_end + 1):
        try:
            run_book(book_id, stats, problems)
        except Exception as e:
            print(f"\n❌ 卷书 {book_id} 初始化失败：{e}")
            stats["failed"] += 1
            problems.append({
                "book_id": book_id,
                "abbr": "???",
                "chapter": "???",
                "detail": str(e)
            })

    total = time.time() - t0

    print(f"\n{'='*60}")
    print(f"🎉 全部完成")
    print(f"✅ 成功：{stats['ok']}")
    print(f"⏭️  跳过：{stats['skipped']}")
    print(f"❌ 失败：{stats['failed']}")
    print(f"⏱ 总耗时：{total:.2f}s")
    print(f"{'='*60}")

    if problems:
        print(f"\n🚨 问题章节汇总（共 {len(problems)} 处）")
        for item in problems:
            print(f"\n--- {item['abbr']} {item['chapter']} (book_id={item['book_id']}) ---")
            lines = item['detail'].strip().splitlines()
            tail = lines[-20:] if len(lines) > 20 else lines
            for line in tail:
                print(line)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：python w_00_highlight_for_book.py <book_start> <book_end>")
        print("示例：python w_00_highlight_for_book.py 1 5")
        sys.exit(1)

    main(int(sys.argv[1]), int(sys.argv[2]))