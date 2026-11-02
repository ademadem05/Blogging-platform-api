import json
import sqlite3
from datetime import datetime, timezone

DB_PATH = "blog.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                tags TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
    """)    

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_post(post_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    return row_to_post(row) if row else None

def row_to_post(row):
    return{
        "id" : row["id"],
        "title" : row["title"],
        "content" : row["content"],
        "category" : row["category"],
        "tags" : json.loads(row["tags"]),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def create_post(title, content, category, tags):
    timestamp = now()

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO posts (title, content, category, tags, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (title, content, category, json.dumps(tags), timestamp, timestamp),
        )
        post_id = cursor.lastrowid
    return get_post(post_id)

def get_all_posts(term=None):
    with get_connection() as conn:
        if term:
            pattern = f"%{term}%"
            rows = conn.execute(
                "SELECT * FROM posts "
                "WHERE title LIKE ? OR content LIKE ? OR category LIKE ? "
                "ORDER BY id",
                (pattern, pattern, pattern)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM posts ORDER BY id").fetchall()
    return [row_to_post(row) for row in rows]


def update_post(post_id, title, content, category, tags):
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE posts SET title = ?, content = ?, category = ?, tags = ?, updated_at = ? WHERE id = ?",
             (title, content, category, json.dumps(tags), now(), post_id)
        )
    if cursor.rowcount == 0:
        return None
    else:
        return get_post(post_id,)

def delete_post(post_id):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM posts WHERE id = ?", (post_id,)
        )
        return cursor.rowcount > 0 



def main():
    init_db()
    post = create_post("My First Post", "Hello from SQLite!", "Technology", ["Tech", "Python"])
    print("Created:", post)
    print("All:", get_all_posts())
    print("Search 'tech':", get_all_posts("tech"))
    print("Missing:", get_post(999))



if __name__ == "__main__":
    main()