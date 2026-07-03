#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
w_00_highlight_for_chapter.py
完整工作流：为指定 book_id + chapter 执行高亮所需全部步骤
防御机制：若目标 JSON 已存在，直接跳过
用法：
    python w_00_highlight_for_chapter.py <book_id> <chapter>
"""

import sys
import subprocess
import sqlite3
import os
import time

DB_PATH = "db/bible.db"
OUTPUT_JSON_DIR = "static/json"

SCRIPTS = {
    "generate_tokens": "w_01_generate_tokens_for_chapter.py",
    "mp3_to_wav":     "w_02_mp3_to_wav_for_chapter.py",
    "force_align":    "w_03_forcealign_for_chapter.py",
    "timestamps":     "w_04_generate_timestamps_for_chapter.py",
    "json":            "w_05_generate_json_for_chapter.py",
}


def get_book_abbr(book_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT abbr_en FROM book WHERE id = ?", (book_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise ValueError(f"book_id={book_id} 不存在")
    return row[0]


def build_json_path(book_id: int, abbr: str, chapter: int) -> str:
    filename = f"{str(book_id).zfill(2)}_{abbr}_{str(chapter).zfill(3)}.json"
    return os.path.join(OUTPUT_JSON_DIR, filename)


def run_step(step_name: str, book_id: int, chapter: int):
    script = SCRIPTS[step_name]
    print(f"\n{'='*60}")
    print(f"▶ 步骤：{step_name}")
    print(f"  脚本：{script}")
    print(f"{'='*60}")

    start = time.time()
    result = subprocess.run(
        ["python", script, str(book_id), str(chapter)]
    )
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"\n❌ 步骤失败：{step_name}（耗时 {elapsed:.2f}s）")
        sys.exit(1)

    print(f"✅ 步骤完成：{step_name}（耗时 {elapsed:.2f}s）")


def main(book_id: int, chapter: int):
    abbr = get_book_abbr(book_id)

    json_path = build_json_path(book_id, abbr, chapter)

    # ✅ 防御检查
    if os.path.exists(json_path):
        print(f"✅ 已存在 JSON 文件：{json_path}")
        print("⏭️ 无需重复操作，直接退出")
        return

    print(f"\n📖 开始完整流程：{abbr} {chapter}")
    print(f"   book_id = {book_id}, chapter = {chapter}")

    t0 = time.time()

    run_step("generate_tokens", book_id, chapter)
    run_step("mp3_to_wav",     book_id, chapter)
    run_step("force_align",    book_id, chapter)
    run_step("timestamps",     book_id, chapter)
    run_step("json",           book_id, chapter)

    total = time.time() - t0
    print(f"\n🎉 全部完成：{abbr} {chapter}")
    print(f"⏱ 总耗时：{total:.2f}s")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：python w_00_highlight_for_chapter.py <book_id> <chapter>")
        print("示例：python w_00_highlight_for_chapter.py 2 32")
        sys.exit(1)

    main(int(sys.argv[1]), int(sys.argv[2]))