#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
w_00_highlight_for_book.py
整卷书工作流：读取 book 表 → 获取 max_chapter → 逐章运行章节流程
已存在 JSON 的章节自动跳过
用法：
    python w_00_highlight_for_book.py <book_id>
"""

import sys
import subprocess
import sqlite3
import os
import time

DB_PATH = "db/bible.db"
OUTPUT_JSON_DIR = "static/json"
CHAPTER_SCRIPT = "w_00_highlight_for_chapter.py"


def get_book_info(book_id: int):
    """
    返回:
      abbr_en, max_chapter
    """
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

    # ✅ 防御检查：JSON 已存在就跳过
    if os.path.exists(json_path):
        print(f"⏭️  已存在，跳过：{abbr} {chapter}")
        return "skipped"

    print(f"\n▶ 开始处理：{abbr} {chapter}")

    start = time.time()
    result = subprocess.run(
        ["python", CHAPTER_SCRIPT, str(book_id), str(chapter)]
    )
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"❌ 失败：{abbr} {chapter}（耗时 {elapsed:.2f}s）")
        return "failed"

    print(f"✅ 完成：{abbr} {chapter}（耗时 {elapsed:.2f}s）")
    return "ok"


def main(book_id: int):
    abbr, max_chapter = get_book_info(book_id)

    print(f"\n📖 开始整卷流程：{abbr}（共 {max_chapter} 章）")
    print(f"   book_id = {book_id}")

    t0 = time.time()

    stats = {
        "ok": 0,
        "skipped": 0,
        "failed": 0,
    }

    for chapter in range(1, max_chapter + 1):
        status = run_chapter(book_id, abbr, chapter)
        stats[status] += 1

    total = time.time() - t0

    print(f"\n🎉 整卷完成：{abbr}")
    print(f"✅ 成功：{stats['ok']}")
    print(f"⏭️  跳过：{stats['skipped']}")
    print(f"❌ 失败：{stats['failed']}")
    print(f"⏱ 总耗时：{total:.2f}s")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python w_00_highlight_for_book.py <book_id>")
        print("示例：python w_00_highlight_for_book.py 2")
        sys.exit(1)

    main(int(sys.argv[1]))