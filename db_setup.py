# db_setup.py
import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create the users table
# The 'username' column is set to be unique to prevent duplicates.
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
)
''')

print("Database and 'users' table created successfully.")

# Commit the changes and close the connection
conn.commit()
conn.close()
