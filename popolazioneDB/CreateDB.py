import sqlite3

con= sqlite3.connect("ChessPositions.db")
cur= con.cursor()

cur.execute("CREATE TABLE position(id INTEGER, fen TEXT, binary BLOB, eval FLOAT)")
