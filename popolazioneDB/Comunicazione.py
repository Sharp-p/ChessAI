import chess
import chess.svg

# Supponiamo che tu abbia una funzione che prenda un FEN e restituisca una valutazione.
def evaluate_position(fen):
    # Qui chiamo il modello per valutare la posizione data dal FEN.
    # Restituisco un valore casuale per esempio.
    import random
    return random.uniform(0, 1)

def find_best_moves(fen, top_n=3):
    board = chess.Board(fen)
    legal_moves = list(board.legal_moves)

    move_evaluations = []
    for move in legal_moves:
        board.push(move)
        new_fen = board.fen()
        evaluation = evaluate_position(new_fen)
        move_evaluations.append((move, evaluation))
        board.pop()

    # Ordina le mosse per valutazione decrescente
    move_evaluations.sort(key=lambda x: x[1], reverse=True)

    # Prendi le prime `top_n` mosse
    best_moves = move_evaluations[:top_n]
    return best_moves

def generate_svg_with_best_moves(fen, top_moves, output_file='best_moves.svg'):
    board = chess.Board(fen)
    # Crea un set di caselle di destinazione delle migliori mosse
    squares = [move.to_square for move, _ in top_moves]
    # Evidenzia le caselle di destinazione
    svg_board = chess.svg.board(board, squares=squares)
    with open(output_file, 'w') as f:
        f.write(svg_board)

# Esempio di utilizzo
fen = "r1b1k2B/1pp1qp2/2n1p2p/8/4Q1P1/b7/p1PP1P1P/K2R1BNR w q - 2 15"
top_moves = find_best_moves(fen)

# Stampa le migliori mosse
for move, evaluation in top_moves:
    print(f"Mossa: {move}, Valutazione: {evaluation}")

# Generare l'SVG con le migliori mosse evidenziate
generate_svg_with_best_moves(fen, top_moves)
