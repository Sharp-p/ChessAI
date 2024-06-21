import sqlite3


#====== SELECT ======

con= sqlite3.connect("ChessPositions.db")
cur= con.cursor()

cur.execute("SELECT * FROM position")
for row in cur: print(row)

con.close()