import sqlite3

con= sqlite3.connect("ChessPositions.db")
cur= con.cursor()
#====== SELECT ======

#cur.execute("SELECT * FROM position")
#for row in cur: print(row)

#====== DELETE ======

""" cur.execute("DELETE FROM position")
con.commit()
 """

#====== COUNT ======

#cur.execute("SELECT COUNT(*) FROM position")
#print(cur.fetchone())

#====== CLEANING DATA ======

#cur.execute("DELETE FROM position WHERE eval is null")
#con.commit()

cur.execute("SELECT * FROM position WHERE id=1")
print(cur.fetchone())


con.close()