import zstandard as zstd
import chess.pgn
from bitstring import BitArray
import sqlite3
from sqlite3 import Error

'''Le partite su python-chess sono organizzati come alberi, 
ogni nodo è uno stato della scacchiera, 
ogni arco a scendere è la mossa che porta allo stato successivo, 
un Game è un nodo (radice) di un'albero (partita) e estende GameNode,
i ChildNode sono i nodi successivi che rappresentano lo stato della scacchiera
durante la partita'''

con= sqlite3.connect("ChessPositions.db")
cur= con.cursor()


with zstd.open('popolazioneDB/\
lichess_db_standard_rated_2023-03.pgn.zst', 'r') as file:
        node= chess.pgn.read_game(file)#Game della prima partita del file
        counter_games = 0
        movesId= 0
        
        with con:        
        
            while node != None:#itero sui Game
                board= node.board()
                node= node.next()#nodo successivo sull'albero della partita
                
                if node != None and node.eval() != None:
                    counter_games+= 1
                    
                    while node != None:#itero sui ChildNodes della partita
                        #metto la mossa che mi ha portato al 
                        # GameNode attuale sulla board
                        board.push(node.move)
                        bitboards= ''
                        movesId+= 1
                        
                        #calcolo la board per ogni tipo di pezzo (sia bianco che nero)
                        # sotto forma di bitboard
                        pieces= board.pieces(chess.PAWN, chess.WHITE)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        pieces= board.pieces(chess.BISHOP, chess.WHITE)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        pieces= board.pieces(chess.KNIGHT, chess.WHITE)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        pieces= board.pieces(chess.ROOK, chess.WHITE)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        pieces= board.pieces(chess.QUEEN, chess.WHITE)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        pieces= board.pieces(chess.KING, chess.WHITE)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        pieces= board.pieces(chess.PAWN, chess.BLACK)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        pieces= board.pieces(chess.BISHOP, chess.BLACK)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        pieces= board.pieces(chess.KNIGHT, chess.BLACK)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        pieces= board.pieces(chess.ROOK, chess.BLACK)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        pieces= board.pieces(chess.QUEEN, chess.BLACK)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        pieces= board.pieces(chess.KING, chess.BLACK)
                        temp= BitArray(bin= bin(pieces))
                        bitboards= bitboards + temp.bin.zfill(64)
                        
                        #stringa che mi dice a chi tocca muovere w=1 b=0
                        binary_turn= str(int(node.turn()))
                        
                        #non includo nel dataset queste informazioni perché 
                        # quando andrà ad eseguire non gli verranno fornite
                        """ #stringa che mi fa una corrispondenza tra la presenza delle
                        # lettere KQkq e 1 e 0, in caso di prensenza o assenza
                        castling_rights= board.castling_xfen()
                        binary_castling= "0000"
                        for x in castling_rights:
                            match x:
                                case 'K':
                                    binary_castling= "1000"
                                case 'Q':
                                    binary_castling= binary_castling[:1]+"100" 
                                case 'k':
                                    binary_castling= binary_castling[:2]+"10"
                                case 'q':
                                    binary_castling= binary_castling[:3]+"1"
                        
                        #ottengo la stringa binaria che rappresenta l'intero che indica
                        # la casella della scacchiera
                        if board.has_legal_en_passant():

                            binary_square= "{0:b}".format(board.ep_square)
                            binary_square= binary_square.zfill(6)
                        else:
                            binary_square= "000000"

                        #ottengo la stringa binaria che rappresenta 
                        # il numero di semimosse (per la regola delle 50 semimosse)
                        binary_ply= "{0:b}".format(board.halfmove_clock)
                        binary_ply= binary_ply.zfill(6)

                        #ottengo la stringa binaria che rappresenta il numero di mosse
                        binary_moves= "{0:b}".format(board.fullmove_number)
                        binary_moves= binary_moves.zfill(8)
                         """
                        #FEN parziale in binario
                        binary_fen= bitboards + binary_turn
                        
                        #evaluation
                        eval= node.eval().white().score(mate_score= 32765) if node.eval() != None else None

                        #popolamento del db
                        try:
                            cur.execute("INSERT INTO position VALUES(?, ?, ?, ?)", 
                                        (movesId, board.fen(), binary_fen, eval))
                        except Error as e:
                            print(f"Qualcosa è andato storto. ({e})")

                        node= node.next()#vado allo stato, ChildNode, successivo

                    if (counter_games % 10) == 0:
                        print(f'\n============= PARTITA {counter_games} =============')

                node= chess.pgn.read_game(file)#Game della partita successiva del file
con.close()
