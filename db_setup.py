# db_setup.py
import sqlite3

# Connect to the database file (it will be created if it doesn't exist)
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create the 'users' table if it doesn't already exist
# This table will store a unique ID, the username, and the hashed password.
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
)
''')

print("Database 'users.db' and table 'users' are ready.")

# Save the changes and close the connection
conn.commit()
conn.close()
