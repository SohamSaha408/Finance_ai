# create_user.py
import json
import bcrypt

USERS_FILE = "users.json"
username = input("Enter new username: ")
password = input("Enter new password: ")

# Hash the password
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Load existing users or create a new dictionary
try:
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    users = {}

# Add the new user
users[username] = hashed_password

# Save the updated user dictionary to the file
with open(USERS_FILE, 'w') as f:
    json.dump(users, f, indent=4)

print(f"User '{username}' was successfully added to {USERS_FILE}")
