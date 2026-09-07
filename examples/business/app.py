import sqlite3
from contextlib import closing

class Notes:
    def __init__(self, path):
        self.path = path
        with closing(sqlite3.connect(path)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL)")

    def create(self, text):
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if not text.strip():
            raise ValueError("text must not be blank")
        with closing(sqlite3.connect(self.path)) as db, db:
            cursor = db.execute("INSERT INTO notes (text) VALUES (?)", (text,))
            return cursor.lastrowid

    def list(self):
        with closing(sqlite3.connect(self.path)) as db:
            return db.execute("SELECT id,text FROM notes ORDER BY id").fetchall()
