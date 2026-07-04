#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_timestamps_for_chapter.py
从 TextGrid 生成 timestamps，并校验一致性
支持 --auto-rollback 非交互模式
"""

import re
import sqlite3
import os
import sys
import shutil
from datetime import datetime
import argparse  # 新增 argparse 用于解析参数

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
    filename = f"{book_id:02d}_{book_abbr}_{chapter:03d}_en.TextGrid"
    filepath = os.path.join(TEXTGRID_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ 找不到 TextGrid：{filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

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


def split_word(text: str):
    final_words = []

    raw_words = text.split()
    for w in raw_words:
        # 同时支持 ' 和 -
        if "'" in w or "-" in w:
            parts = [w]
            for sep in ["'", "-"]:
                new_parts = []
                for p in parts:
                    new_parts.extend(p.split(sep))
                parts = new_parts
            parts = [p for p in parts if p]
            final_words.extend(parts)
        else:
            final_words.append(w)

    return final_words


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

            align_id = f"{book_id:02d}_{book_abbr}_{chapter:03d}__{word_seq:04d}"

            cursor.execute(
                "INSERT INTO timestamps (id, chapter, word_seq, word, start_time, end_time) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (align_id, chapter, word_seq, w, start_ms, end_ms)
            )

    conn.commit()
    conn.close()
    print(f"✅ 共插入 {word_seq} 条 timestamps")


def check_and_rollback(book_id: int, book_abbr: str, chapter: int, backup_path: str, auto_rollback: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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

    print(f"\n❌ 发现 {len(mismatches)} 处不一致：")
    for r in mismatches[:5]:
        print(f"  {r[0]:30s} | timestamps.word={r[1]} | tokens.token={r[2]}")
    if len(mismatches) > 5:
        print(f"  ...（共 {len(mismatches)} 条）")

    # ============ 核心改动：非交互自动回滚 ============
    if auto_rollback:
        print(f"⚠️ 非交互模式：自动执行回滚")
        conn.close()
        shutil.copy(backup_path, DB_PATH)
        print(f"🔄 已回滚数据库")
        # 以非零退出，让上层调度感知到失败
        sys.exit(1)
    else:
        # 保留原有交互逻辑
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
    parser = argparse.ArgumentParser()
    parser.add_argument("book_id", type=int)
    parser.add_argument("chapter", type=int)
    parser.add_argument("--auto-rollback", action="store_true", help="非交互模式，自动回滚")
    args = parser.parse_args()

    book_id = args.book_id
    chapter = args.chapter
    auto_rollback = args.auto_rollback

    book_abbr = get_book_info(book_id)

    print(f"📖 处理：{book_abbr} {chapter}")

    backup_path = backup_database()
    matches = parse_textgrid(book_id, book_abbr, chapter)
    fill_timestamps(book_id, book_abbr, chapter, matches)
    check_and_rollback(book_id, book_abbr, chapter, backup_path, auto_rollback)