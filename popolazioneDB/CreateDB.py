import sqlite3

con= sqlite3.connect("Progetto/ChessPositions.db")
cur= con.cursor()

cur.execute("CREATE TABLE position(id, fen, binary, eval)")
