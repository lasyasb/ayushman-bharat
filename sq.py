import sqlite3

conn = sqlite3.connect("fraud.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(claims);")
print(cursor.fetchall())


conn.close()