# 默认书卷：玛窦福音 47 章
DEFAULT_BOOK_ID = 47
DEFAULT_CHAPTER = 1

import os
import sqlite3
from flask import Flask, render_template, g, jsonify

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "db", "bible.db")

app = Flask(__name__)

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

@app.route("/")
def index():
    db = get_db()
    books = db.execute(
        "SELECT id, name_cn FROM book ORDER BY order_index"
    ).fetchall()
    return render_template(
        "index.html",
        books=books,
        default_book_id=DEFAULT_BOOK_ID,
        default_chapter=DEFAULT_CHAPTER
    )

@app.route("/chapters/<int:book_id>")
def chapters(book_id):
    db = get_db()
    rows = db.execute(
        "SELECT DISTINCT chapter FROM verse WHERE book_id = ? ORDER BY chapter",
        (book_id,)
    ).fetchall()
    return jsonify([r["chapter"] for r in rows])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)