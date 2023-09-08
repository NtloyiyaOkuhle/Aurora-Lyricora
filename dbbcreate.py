import sqlite3

# Create a connection to the database (this will create a new database file if it doesn't exist)
conn = sqlite3.connect('reviews.db')
cursor = conn.cursor()

# Define the schema for the reviews table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
