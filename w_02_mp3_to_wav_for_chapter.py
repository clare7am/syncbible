#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
mp3_to_wav_chapter.py
将指定 book_id + chapter 的 mp3 转换为 wav
文件名格式：02_Ex_032_en
"""

import os
import subprocess
import sys
import sqlite3
import time

MP3_DIR = "outputs/mp3"
WAV_DIR = "outputs/wav"
SAMPLE_RATE = "16000"

DB_PATH = "db/bible.db"


def get_book_abbr(book_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT abbr_en FROM book WHERE id = ?", (book_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise ValueError(f"book_id={book_id} 不存在于 book 表")
    return row[0]


def convert_mp3_to_wav(book_id: int, chapter: int):
    book_abbr = get_book_abbr(book_id)

    base_name = f"{book_id:02d}_{book_abbr}_{chapter:03d}_en"

    mp3_path = os.path.join(MP3_DIR, f"{base_name}.mp3")
    wav_path = os.path.join(WAV_DIR, f"{base_name}.wav")

    if not os.path.isfile(mp3_path):
        raise FileNotFoundError(f"❌ 找不到 MP3：{mp3_path}")

    if os.path.isfile(wav_path):
        print(f"⏭️ 已存在，跳过：{base_name}.wav")
        return

    os.makedirs(WAV_DIR, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-loglevel", "error",
        "-i", mp3_path,
        "-ar", SAMPLE_RATE,
        "-ac", "1",
        wav_path
    ]

    print(f"🎬 转换中：{base_name}.mp3 → {base_name}.wav")
    start = time.time()
    subprocess.run(cmd, check=True)
    print(f"✅ 完成：{base_name}.wav （{time.time() - start:.2f}s）")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：python mp3_to_wav_chapter.py <book_id> <chapter>")
        print("示例：python mp3_to_wav_chapter.py 2 32")
        sys.exit(1)

    book_id = int(sys.argv[1])
    chapter = int(sys.argv[2])

    convert_mp3_to_wav(book_id, chapter)