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

    # ✅ 防御检查：JSON 已存在就跳过
    if os.path.exists(json_path):
        print(f"⏭️  已存在，跳过：{abbr} {chapter}")
        return "skipped", None

    print(f"\n▶ 开始处理：{abbr} {chapter}")

    start = time.time()
    
    # 核心改动：捕获子进程的 stderr 和 returncode
    result = subprocess.run(
        ["python", CHAPTER_SCRIPT, str(book_id), str(chapter)],
        capture_output=True,
        text=True
    )
    
    elapsed = time.time() - start

    # 打印子进程输出，方便现场排查
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print(f"❌ 失败：{abbr} {chapter}（耗时 {elapsed:.2f}s）")
        # 返回失败状态和 stderr 信息，供顶层汇总
        return "failed", result.stderr
        
    print(f"✅ 完成：{abbr} {chapter}（耗时 {elapsed:.2f}s）")
    return "ok", None


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

    # 核心改动：收集问题章节
    problems = []

    for chapter in range(1, max_chapter + 1):
        try:
            status, detail = run_chapter(book_id, abbr, chapter)
            stats[status] += 1
            
            # 只有真正失败的才记录
            if status == "failed":
                problems.append({
                    "chapter": chapter,
                    "detail": detail
                })
                
        except Exception:
            # 防止极端情况导致整卷流程中断
            stats["failed"] += 1
            problems.append({
                "chapter": chapter,
                "detail": traceback.format_exc()
            })

    total = time.time() - t0

    print(f"\n🎉 整卷完成：{abbr}")
    print(f"✅ 成功：{stats['ok']}")
    print(f"⏭️  跳过：{stats['skipped']}")
    print(f"❌ 失败：{stats['failed']}")
    print(f"⏱ 总耗时：{total:.2f}s")

    # ============ 核心改动：统一打印问题章节报告 ============
    if problems:
        print(f"\n🚨 问题章节汇总（共 {len(problems)} 章）")
        for item in problems:
            print(f"\n--- {abbr} {item['chapter']} ---")
            # 打印 stderr 或异常堆栈的最后几行，避免刷屏
            lines = item['detail'].strip().splitlines()
            tail = lines[-20:] if len(lines) > 20 else lines
            for line in tail:
                print(line)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python w_00_highlight_for_book.py <book_id>")
        print("示例：python w_00_highlight_for_book.py 2")
        sys.exit(1)

    main(int(sys.argv[1]))