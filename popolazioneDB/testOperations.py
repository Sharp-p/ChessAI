import sqlite3

con= sqlite3.connect("ChessPositions.db")
cur= con.cursor()

#====== SELECT ======

cur.execute("SELECT * FROM position")
for row in cur: print(row)

#====== DELETE ======

""" cur.execute("DELETE FROM position")
con.commit()
 """

con.close()