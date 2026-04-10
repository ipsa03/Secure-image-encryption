import sqlite3

# Connect to database (creates file automatically)
conn = sqlite3.connect('database.db')

# Create table
conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
''')

conn.close()

print("Database created successfully!")