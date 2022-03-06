import sqlite3

connection = sqlite3.connect('post_flack.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content, owner) VALUES (?, ?, ?)",
            ('First Post', 'Content for the first post', 1)
            )

cur.execute("INSERT INTO posts (title, content, owner) VALUES (?, ?, ?)",
            ('Second Post', 'Content for the second post', 2)
            )

connection.commit()
connection.close()