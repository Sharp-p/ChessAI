import sqlite3

con= sqlite3.connect("ChessPositions.db")
cur= con.cursor()

cur.execute("CREATE TABLE position(id, fen, binary, eval)")
