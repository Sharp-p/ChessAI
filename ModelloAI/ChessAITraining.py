from peewee import *
import base64

db= SqliteDatabase('ChessPositions.db')

class Evaluations(Model):
    id= IntegerField()
    fen= TextField()
    binary= BlobField()
    eval= FloatField()

    class Meta:
        database= db