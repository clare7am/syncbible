import os
import sqlite3
from flask import Flask, render_template, g, jsonify

# ========= 基础配置 =========
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "db", "bible.db")

app = Flask(__name__)

# ========= 数据库 =========
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db:
        db.close()


# ========= 页面 =========
@app.route("/")
def index():
    db = get_db()
    books = db.execute(
        "SELECT id, name_cn FROM book ORDER BY id"
    ).fetchall()

    return render_template("index.html", books=books)


# ========= 接口 =========
@app.route("/chapters/<int:book_id>")
def chapters(book_id):
    """
    获取某卷书的所有章节
    """
    db = get_db()
    rows = db.execute(
        """
        SELECT DISTINCT chapter, chapter_title
        FROM verses
        WHERE book_id = ?
        ORDER BY chapter
        """,
        (book_id,)
    ).fetchall()

    return jsonify([
        {
            "chapter": r["chapter"],
            "chapter_title": r["chapter_title"]
        }
        for r in rows
    ])


@app.route("/verses/<int:book_id>/<int:chapter>")
def verses(book_id, chapter):
    """
    获取某章经文（纯文本）
    """
    db = get_db()
    rows = db.execute(
        """
        SELECT verse, text_en, text_cn
        FROM verses
        WHERE book_id = ? AND chapter = ?
        ORDER BY verse
        """,
        (book_id, chapter)
    ).fetchall()

    return jsonify([
        {
            "verse": r["verse"],
            "text_en": r["text_en"],
            "text_cn": r["text_cn"]
        }
        for r in rows
    ])


@app.route("/has_tokens/<int:book_id>/<int:chapter>")
def has_tokens(book_id, chapter):
    db = get_db()
    row = db.execute(
        """
        SELECT 1
        FROM tokens
        WHERE book_id = ? AND chapter = ?
        LIMIT 1
        """,
        (book_id, chapter)
    ).fetchone()

    return jsonify({
        "has_tokens": row is not None
    })

@app.route("/verses_with_words/<int:book_id>/<int:chapter>")
def verses_with_words(book_id, chapter):
    db = get_db()

    rows = db.execute("""
        SELECT
            v.verse,
            v.text_cn,
            t.token       AS word,
            t.type,
            t.entity_key,
            t.align_id,
            t.token_id,
            ts.start_time,
            ts.end_time
        FROM verses v
        LEFT JOIN tokens t
            ON v.book_id = t.book_id
           AND v.chapter = t.chapter
           AND v.verse   = t.verse
        LEFT JOIN timestamps ts
            ON t.align_id = ts.id
        WHERE v.book_id = ?
          AND v.chapter = ?
        ORDER BY v.verse, t.token_id
    """, (book_id, chapter)).fetchall()

    result = []
    current_verse = None
    verse_obj = None

    for r in rows:
        if current_verse != r["verse"]:
            verse_obj = {
                "verse": r["verse"],
                "text_cn": r["text_cn"],
                "words": []
            }
            result.append(verse_obj)
            current_verse = r["verse"]

        if r["word"]:  # 有些 verse 可能没有 token
            verse_obj["words"].append({
                "word": r["word"],
                "type": r["type"] or "",
                "entity_key": r["entity_key"] or "",
                "align_id": r["align_id"] or "",
                "start": r["start_time"] or 0,
                "end": r["end_time"] or 0
            })

    return jsonify(result)


# ========= 启动 =========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)