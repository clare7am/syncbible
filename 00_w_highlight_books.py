#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
w_00_highlight_for_books_fast.py
高性能合并版工作流（单进程 / SQLite 长连接 / 完整性校验）
用法：
    python w_00_highlight_for_books_fast.py <book_start> <book_end>
"""

import os
import sys
import time
import json
import re
import shutil
import sqlite3
import subprocess
from datetime import datetime
from typing import List, Tuple

# ===== 注入 MFA (aligner conda env) =====
try:
    conda_base = subprocess.check_output(
        ["conda", "info", "--base"], text=True
    ).strip()
    aligner_bin = os.path.join(conda_base, "envs", "aligner", "bin")
    os.environ["PATH"] = aligner_bin + os.pathsep + os.environ["PATH"]
except Exception as e:
    print("⚠️ 无法注入 aligner 环境，MFA 可能无法运行")
    print(e)

# ===== 路径配置 =====
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "bible.db")
OUTPUT_JSON_DIR = os.path.join(BASE_DIR, "outputs", "json")
WAV_DIR = os.path.join(BASE_DIR, "outputs", "wav")
MP3_DIR = os.path.join(BASE_DIR, "outputs", "mp3")
TXT_DIR = os.path.join(BASE_DIR, "outputs", "plaintext")
CORPUS_DIR = os.path.join(BASE_DIR, "corpus")
ALIGN_OUT = os.path.join(BASE_DIR, "outputs", "forcealign")
BACKUP_DIR = os.path.join(BASE_DIR, "db", "backups")

SAMPLE_RATE = "16000"

# ===== MFA =====
MFA_DICT = os.path.expanduser(
    "~/Documents/MFA/pretrained_models/dictionary/english_us_arpa.dict"
)
MFA_ACOUSTIC = os.path.expanduser(
    "~/Documents/MFA/pretrained_models/acoustic/english_us_arpa.zip"
)

# ===== 全局统计 =====
stats = {"ok": 0, "skipped": 0, "failed": 0}
problems = []


# ============================================================
# SQLite 工具
# ============================================================

def open_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-64000")
    return conn


def vacuum_db(conn):
    print("♻️  VACUUM database ...")
    conn.execute("VACUUM")


# ============================================================
# 通用工具
# ============================================================

def get_book_info(conn, book_id: int):
    cur = conn.cursor()
    cur.execute("SELECT abbr_en, max_chapter FROM book WHERE id = ?", (book_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"book_id={book_id} 不存在")
    return row[0], row[1]


def build_json_path(book_id: int, abbr: str, chapter: int) -> str:
    name = f"{str(book_id).zfill(2)}_{abbr}_{str(chapter).zfill(3)}.json"
    return os.path.join(OUTPUT_JSON_DIR, name)


def build_wav_path(book_id: int, abbr: str, chapter: int) -> str:
    return os.path.join(WAV_DIR, f"{book_id:02d}_{abbr}_{chapter:03d}_en.wav")


def build_mp3_path(book_id: int, abbr: str, chapter: int) -> str:
    return os.path.join(MP3_DIR, f"{book_id:02d}_{abbr}_{chapter:03d}_en.mp3")


def build_textgrid_path(book_id: int, abbr: str, chapter: int) -> str:
    return os.path.join(ALIGN_OUT, f"{book_id:02d}_{abbr}_{chapter:03d}_en.TextGrid")


# ============================================================
# Step 1：Generate Tokens
# ============================================================

def segment_english(text: str) -> List[Tuple[str, str]]:
    tokens = []
    cur = ""
    cur_type = None

    def flush():
        nonlocal cur, cur_type
        if cur:
            tokens.append((cur, cur_type))
            cur = ""
            cur_type = None

    for ch in text:
        if ch.isalpha():
            t = "word"
        elif ch.isdigit():
            t = "number"
        elif ch.isspace():
            t = "space"
        else:
            t = "punct"

        if t != cur_type:
            flush()
            cur_type = t
        cur += ch
    flush()
    return tokens


def step_generate_tokens(conn, book_id: int, abbr: str, chapter: int):
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM tokens WHERE book_id=? AND chapter=?",
        (book_id, chapter)
    )
    if cur.fetchone()[0] > 0:
        print("⏭️  tokens 已存在")
        return

    cur.execute("""
        SELECT v.id, v.verse, v.text_en
        FROM verses v
        WHERE v.book_id=? AND v.chapter=?
          AND v.text_en IS NOT NULL
        ORDER BY v.verse
    """, (book_id, chapter))

    verses = cur.fetchall()
    token_rows = []
    word_seq = 0

    for verse_id, verse_num, text_en in verses:
        tokens = segment_english(text_en)
        for idx, (token, token_type) in enumerate(tokens, 1):
            token_id = f"{abbr}.{chapter}.{verse_num}.{idx}"
            align_id = None
            if token_type == "word":
                word_seq += 1
                align_id = f"{book_id:02d}_{abbr}_{chapter:03d}__{word_seq:04d}"

            token_rows.append((
                token_id, book_id, chapter, verse_num,
                idx, token, token_type, align_id
            ))

    cur.executemany("""
        INSERT INTO tokens
        (id, book_id, chapter, verse, token_id, token, type, align_id)
        VALUES (?,?,?,?,?,?,?,?)
    """, token_rows)

    conn.commit()
    print(f"✅ tokens inserted: {len(token_rows)}")


# ============================================================
# Step 2：MP3 → WAV
# ============================================================

def step_mp3_to_wav(book_id: int, abbr: str, chapter: int):
    wav_path = build_wav_path(book_id, abbr, chapter)

    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
        print("⏭️  wav 已存在")
        return

    mp3_path = build_mp3_path(book_id, abbr, chapter)
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"❌ 缺少 MP3: {mp3_path}")

    os.makedirs(WAV_DIR, exist_ok=True)

    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", mp3_path,
        "-ar", SAMPLE_RATE, "-ac", "1",
        wav_path
    ], check=True)

    print("✅ wav 转换完成")


# ============================================================
# Step 3：Force Align
# ============================================================

def step_force_align(book_id: int, abbr: str, chapter: int):
    tg_path = build_textgrid_path(book_id, abbr, chapter)

    if os.path.exists(tg_path) and os.path.getsize(tg_path) > 0:
        print("⏭️  TextGrid 已存在")
        return

    wav_path = build_wav_path(book_id, abbr, chapter)
    txt_path = os.path.join(TXT_DIR, f"{book_id:02d}_{abbr}_{chapter:03d}_en.txt")

    if not os.path.exists(wav_path):
        raise FileNotFoundError("❌ 缺少 WAV")
    if not os.path.exists(txt_path):
        raise FileNotFoundError("❌ 缺少 TXT")

    shutil.copy(wav_path, os.path.join(CORPUS_DIR, os.path.basename(wav_path)))
    shutil.copy(txt_path, os.path.join(CORPUS_DIR, os.path.basename(txt_path)))

    subprocess.run([
        "mfa", "align", CORPUS_DIR,
        MFA_DICT, MFA_ACOUSTIC, ALIGN_OUT,
        "--clean", "--overwrite"
    ], check=True)

    print("✅ 强制对齐完成")


# ============================================================
# Step 4：Timestamps
# ============================================================

def step_timestamps(conn, book_id: int, abbr: str, chapter: int):
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM timestamps WHERE id LIKE ?",
        (f"{book_id:02d}_{abbr}_{chapter:03d}__%",)
    )
    if cur.fetchone()[0] > 0:
        print("⏭️  timestamps 已存在")
        return

    tg_path = build_textgrid_path(book_id, abbr, chapter)
    with open(tg_path, "r", encoding="utf-8") as f:
        content = f.read()

    matches = re.findall(
        r"xmin\s*=\s*([\d.]+)\s*\n"
        r"\s*xmax\s*=\s*([\d.]+)\s*\n"
        r'\s*text\s*=\s*"([^"]*)"',
        content
    )

    word_seq = 0
    for xmin, xmax, text in matches:
        text = text.strip()
        if not text:
            continue

        words = text.replace("-", " ").replace("'", " ").split()
        dur = float(xmax) - float(xmin)
        per = dur / len(words)

        for i, w in enumerate(words):
            word_seq += 1
            start = float(xmin) + i * per
            end = start + per

            align_id = f"{book_id:02d}_{abbr}_{chapter:03d}__{word_seq:04d}"

            cur.execute("""
                INSERT INTO timestamps
                (id, chapter, word_seq, word, start_time, end_time)
                VALUES (?,?,?,?,?,?)
            """, (
                align_id, chapter, word_seq,
                w, int(start * 1000), int(end * 1000)
            ))

    conn.commit()
    print(f"✅ timestamps inserted: {word_seq}")


# ============================================================
# Step 5：Generate JSON
# ============================================================

def step_generate_json(conn, book_id: int, abbr: str, chapter: int):
    json_path = build_json_path(book_id, abbr, chapter)

    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("has_tokens"):
                print("⏭️  JSON 已存在且完整")
                return
        except Exception:
            pass

    cur = conn.cursor()
    rows = cur.execute("""
        SELECT
            v.verse, v.text_cn,
            t.token, t.type, t.entity_key,
            t.align_id, ts.start_time, ts.end_time
        FROM verses v
        LEFT JOIN tokens t
          ON v.book_id=t.book_id AND v.chapter=t.chapter AND v.verse=t.verse
        LEFT JOIN timestamps ts ON t.align_id=ts.id
        WHERE v.book_id=? AND v.chapter=?
        ORDER BY v.verse, t.token_id
    """, (book_id, chapter)).fetchall()

    verses = []
    cur_verse = None
    obj = None

    for r in rows:
        if cur_verse != r[0]:
            obj = {"verse": r[0], "text_cn": r[1], "words": []}
            verses.append(obj)
            cur_verse = r[0]
        if r[2]:
            obj["words"].append({
                "word": r[2],
                "type": r[3] or "",
                "entity_key": r[4] or "",
                "align_id": r[5] or "",
                "start": r[6] or 0,
                "end": r[7] or 0
            })

    payload = {
        "has_tokens": any(len(v["words"]) > 0 for v in verses),
        "verses": verses
    }

    os.makedirs(OUTPUT_JSON_DIR, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("✅ JSON 已生成")


# ============================================================
# 主流程
# ============================================================

def run_chapter(conn, book_id: int, abbr: str, chapter: int):
    print(f"\n▶ {abbr} {chapter}")
    t0 = time.time()

    step_generate_tokens(conn, book_id, abbr, chapter)
    step_mp3_to_wav(book_id, abbr, chapter)
    step_force_align(book_id, abbr, chapter)
    step_timestamps(conn, book_id, abbr, chapter)
    step_generate_json(conn, book_id, abbr, chapter)

    print(f"⏱ {time.time() - t0:.2f}s")


def run_book(conn, book_id: int):
    abbr, max_chapter = get_book_info(conn, book_id)

    for chapter in range(1, max_chapter + 1):
        try:
            run_chapter(conn, book_id, abbr, chapter)
            stats["ok"] += 1
        except Exception as e:
            stats["failed"] += 1
            problems.append({
                "book_id": book_id,
                "abbr": abbr,
                "chapter": chapter,
                "detail": str(e)
            })
            print(f"❌ {abbr} {chapter}: {e}")


def main(book_start: int, book_end: int):
    conn = open_db()
    t0 = time.time()

    for book_id in range(book_start, book_end + 1):
        run_book(conn, book_id)

        if book_id % 10 == 0:
            vacuum_db(conn)

    conn.close()

    print(f"\n🎉 全部完成")
    print(f"✅ {stats['ok']}  ❌ {stats['failed']}")
    print(f"⏱ {time.time() - t0:.2f}s")

    if problems:
        print(f"\n🚨 问题汇总（{len(problems)} 处）")
        for p in problems:
            print(f"  {p['abbr']} {p['chapter']}: {p['detail']}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python w_00_highlight_for_books_fast.py <start> <end>")
        sys.exit(1)

    main(int(sys.argv[1]), int(sys.argv[2]))
