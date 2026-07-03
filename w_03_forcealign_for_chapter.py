#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
force_align_chapter.py
对指定 book_id + chapter 执行 MFA 强制对齐
文件名格式：02_Ex_032_en
"""

import os
import shutil
import subprocess
import sys
import sqlite3

# ===== 目录 =====
WAV_DIR = "outputs/wav"
TXT_DIR = "outputs/plaintext"
CORPUS_DIR = "corpus"
ALIGN_OUT = "outputs/forcealign"

DB_PATH = "db/bible.db"

# ===== MFA 模型路径 =====
dict_path = os.path.expanduser(
    "~/Documents/MFA/pretrained_models/dictionary/english_us_arpa.dict"
)
acoustic_path = os.path.expanduser(
    "~/Documents/MFA/pretrained_models/acoustic/english_us_arpa.zip"
)

# ===== 注入 aligner 环境 =====
conda_prefix = subprocess.check_output(
    ["conda", "info", "--base"], text=True
).strip()
aligner_bin = os.path.join(conda_prefix, "envs", "aligner", "bin")
os.environ["PATH"] = aligner_bin + ":" + os.environ["PATH"]


def get_book_abbr(book_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT abbr_en FROM book WHERE id = ?", (book_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise ValueError(f"book_id={book_id} 不存在于 book 表")
    return row[0]


def prepare_and_align(book_id: int, chapter: int):
    book_abbr = get_book_abbr(book_id)
    base_name = f"{book_id:02d}_{book_abbr}_{chapter:03d}_en"

    wav_path = os.path.join(WAV_DIR, f"{base_name}.wav")
    txt_path = os.path.join(TXT_DIR, f"{base_name}.txt")
    textgrid_path = os.path.join(ALIGN_OUT, f"{base_name}.TextGrid")

    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"❌ 缺少 WAV 文件：{wav_path}")
    if not os.path.exists(txt_path):
        raise FileNotFoundError(f"❌ 缺少 TXT 文件：{txt_path}")

    if os.path.exists(textgrid_path):
        print(f"✅ 已对齐，跳过：{base_name}")
        return

    os.makedirs(CORPUS_DIR, exist_ok=True)
    os.makedirs(ALIGN_OUT, exist_ok=True)

    shutil.copy(wav_path, os.path.join(CORPUS_DIR, f"{base_name}.wav"))
    shutil.copy(txt_path, os.path.join(CORPUS_DIR, f"{base_name}.txt"))

    cmd = [
        "mfa", "align", CORPUS_DIR,
        dict_path,
        acoustic_path,
        ALIGN_OUT,
        "--clean", "--overwrite"
    ]

    print(f"🚀 开始强制对齐：{base_name}")
    subprocess.run(cmd, check=True)
    print(f"🏁 对齐完成：{base_name}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：python force_align_chapter.py <book_id> <chapter>")
        print("示例：python force_align_chapter.py 2 32")
        sys.exit(1)

    book_id = int(sys.argv[1])
    chapter = int(sys.argv[2])

    prepare_and_align(book_id, chapter)