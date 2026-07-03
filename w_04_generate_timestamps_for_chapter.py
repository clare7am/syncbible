#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_timestamps_for_chapter.py
从 TextGrid 生成 timestamps，并校验一致性
"""

import re
import sqlite3
import os
import sys
import shutil
from datetime import datetime

DB_PATH = "db/bible.db"
TEXTGRID_DIR = "outputs/forcealign"
BACKUP_DIR = "db/backups"


# ============ 工具函数 ============

def backup_database():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"bible_{ts}.db")

    shutil.copy(DB_PATH, backup_path)
    print(f"📦 数据库已备份：{backup_path}")
    return backup_path


def get_book_info(book_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT abbr_en FROM book WHERE id = ?", (book_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise ValueError(f"book_id={book_id} 不存在")
    return row[0]


def parse_textgrid(book_id: int, book_abbr: str, chapter: int):
    # ✅ 文件名格式：02_Ex_001_en.TextGrid
    filename = f"{book_id:02d}_{book_abbr}_{chapter:03d}_en.TextGrid"
    filepath = os.path.join(TEXTGRID_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ 找不到 TextGrid：{filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 只提取 item [1]
    item1_pattern = re.compile(
        r"item\s*\[1\]:(.*?)(?=\n\s*item\s*\[\d+\]:|\Z)",
        re.DOTALL
    )
    m = item1_pattern.search(content)
    if not m:
        raise ValueError("❌ 未找到 item [1]")

    interval_pattern = re.compile(
        r"intervals\s*\[\d+\]:\s*\n"
        r"\s*xmin\s*=\s*([\d.]+)\s*\n"
        r"\s*xmax\s*=\s*([\d.]+)\s*\n"
        r'\s*text\s*=\s*"([^"]*)"',
        re.MULTILINE
    )

    return interval_pattern.findall(m.group(1))


def split_word(word: str):
    if word.endswith("'s"):
        return [word[:-2], "s"]
    return [word]


def fill_timestamps(book_id: int, book_abbr: str, chapter: int, matches):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='timestamps'"
    )
    if cursor.fetchone() is None:
        raise RuntimeError("❌ timestamps 表不存在")

    word_seq = 0

    for xmin, xmax, text in matches:
        text = text.strip()
        if not text:
            continue

        words = split_word(text)
        duration = float(xmax) - float(xmin)
        per_word = duration / len(words)

        for i, w in enumerate(words):
            word_seq += 1
            start = float(xmin) + i * per_word
            end = start + per_word

            start_ms = int(round(start * 1000))
            end_ms = int(round(end * 1000))

            # ✅ align_id 格式：02_Ex_001__0001
            align_id = f"{book_id:02d}_{book_abbr}_{chapter:03d}__{word_seq:04d}"

            cursor.execute(
                "INSERT INTO timestamps (id, chapter, word_seq, word, start_time, end_time) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (align_id, chapter, word_seq, w, start_ms, end_ms)
            )

    conn.commit()
    conn.close()
    print(f"✅ 共插入 {word_seq} 条 timestamps")


def check_and_rollback(book_id: int, book_abbr: str, chapter: int, backup_path: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ✅ 前缀格式：02_Ex_001
    id_prefix = f"{book_id:02d}_{book_abbr}_{chapter:03d}"

    cursor.execute(
        """
        SELECT t.id, t.word, tk.token
        FROM timestamps t
        JOIN tokens tk ON t.id = tk.align_id
        WHERE t.id LIKE ?
        """,
        (f"{id_prefix}%",)
    )

    mismatches = []
    for row in cursor.fetchall():
        word = (row[1] or "").strip().lower()
        token = (row[2] or "").strip().lower()
        if word != token:
            mismatches.append(row)

    if not mismatches:
        print(f"✅ 填充完成，检查完毕，所有 word 与 token 一致")
        conn.close()
        return

    # 有不一致
    print(f"\n❌ 发现 {len(mismatches)} 处不一致：")
    for r in mismatches[:5]:
        print(f"  {r[0]:30s} | timestamps.word={r[1]} | tokens.token={r[2]}")
    if len(mismatches) > 5:
        print(f"  ...（共 {len(mismatches)} 条）")

    answer = input("\n是否回滚到备份？(Y/N): ").strip().upper()
    if answer == "Y":
        conn.close()
        shutil.copy(backup_path, DB_PATH)
        print(f"🔄 已回滚数据库")
    else:
        print("⚠️ 未回滚，请手动处理不一致数据")
        conn.close()


# ============ 主流程 ============

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：python generate_timestamps_for_chapter.py <book_id> <chapter>")
        print("示例：python generate_timestamps_for_chapter.py 2 1")
        sys.exit(1)

    book_id = int(sys.argv[1])
    chapter = int(sys.argv[2])

    book_abbr = get_book_info(book_id)

    print(f"📖 处理：{book_abbr} {chapter}")

    # Step 1：备份
    backup_path = backup_database()

    # Step 2：解析 TextGrid
    matches = parse_textgrid(book_id, book_abbr, chapter)

    # Step 3：填充 timestamps
    fill_timestamps(book_id, book_abbr, chapter, matches)

    # Step 4：校验 + 回滚
    check_and_rollback(book_id, book_abbr, chapter, backup_path)