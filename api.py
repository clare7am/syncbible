import os
import sqlite3
from flask import Flask, render_template, g

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
    return render_template("index.html", books=books)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)