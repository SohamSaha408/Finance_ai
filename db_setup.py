# db_setup.py
import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# --- Create the users table (no changes here) ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
)
''')

# --- Add the new watchlist table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ticker TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

print("Database and tables created successfully.")
conn.commit()
conn.close()
