import chess
import chess.svg
import base64
import math
import cairosvg
import cv2
import numpy as np

# Da importare
# from ModelloAI.ChessAiTraining import (?)

from cv.cv import getFen

import sys

# Supponiamo che tu abbia una funzione che prenda un FEN e restituisca una valutazione.
def evaluate_position(fen):
    # Qui dovresti chiamare il tuo modello per valutare la posizione data dal FEN.
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


def generate_svg_with_highlights(fen, top_moves, output_file='chess_board.svg'):
    board = chess.Board(fen)
    # Genera l'SVG della scacchiera
    svg_board = chess.svg.board(board)

    # Colori per le migliori mosse
    colors = ['green', 'yellow', 'red']
    highlights = ""

    # Definizione dei marker delle frecce per ogni colore
    arrow_defs = """
    <defs>
        <marker id="arrowhead-green" markerWidth="5" markerHeight="5" 
                refX="2.5" refY="2.5" orient="auto" fill="green">
            <polygon points="0 0, 5 2.5, 0 5" />
        </marker>
        <marker id="arrowhead-yellow" markerWidth="5" markerHeight="5" 
                refX="2.5" refY="2.5" orient="auto" fill="yellow">
            <polygon points="0 0, 5 2.5, 0 5" />
        </marker>
        <marker id="arrowhead-red" markerWidth="5" markerHeight="5" 
                refX="2.5" refY="2.5" orient="auto" fill="red">
            <polygon points="0 0, 5 2.5, 0 5" />
        </marker>
    </defs>
    """

    marker_length = 5  # Lunghezza del marker della freccia

    for idx, (move, _) in enumerate(top_moves):
        from_square = move.from_square
        to_square = move.to_square
        color = colors[idx]
        arrowhead_id = f"arrowhead-{color}"

        # Calcola le coordinate per le caselle di origine e destinazione
        from_row = 7 - chess.square_rank(from_square)
        from_col = chess.square_file(from_square)
        from_x = from_col * 45 + 37.5
        from_y = from_row * 45 + 37.5

        to_row = 7 - chess.square_rank(to_square)
        to_col = chess.square_file(to_square)
        to_x = to_col * 45 + 37.5
        to_y = to_row * 45 + 37.5

        # Calcola l'angolo della linea
        angle = math.atan2(to_y - from_y, to_x - from_x)

        # Calcola le nuove coordinate finali tenendo conto della lunghezza del marker
        to_x_adjusted = to_x - (marker_length * math.cos(angle))
        to_y_adjusted = to_y - (marker_length * math.sin(angle))

        # Aggiunge una linea con una freccia dalla casella di origine a quella di destinazione
        highlights += f'<line x1="{from_x}" y1="{from_y}" x2="{to_x_adjusted}" y2="{to_y_adjusted}" ' \
                      f'stroke="{color}" stroke-width="5" marker-end="url(#{arrowhead_id})" />'

    # Inserisce gli highlight e le definizioni delle frecce nell'SVG
    svg_board = svg_board.replace('</svg>', f'{arrow_defs}{highlights}</svg>')

    # Salva l'SVG nel file
    with open(output_file, 'w') as f:
        f.write(svg_board)


# Esempio di utilizzo
if __name__ == '__main__':
    assert len(sys.argv) == 3, "Usage: ./main.py filename turn[w/b]"
    assert sys.argv[2] == 'w' or sys.argv[2] == 'b', "Usage: ./main.py filename turn[w,b]"

    filename = sys.argv[1]
    turn = sys.argv[2]

    fen = getFen(filename) + " " + turn

    print(fen)
    top_moves = find_best_moves(fen)

    # Stampa le migliori mosse
    for move, evaluation in top_moves:
        print(f"Mossa: {move}, Valutazione: {evaluation}")

    # Generare l'SVG con le migliori mosse evidenziate
    generate_svg_with_highlights(fen, top_moves)

# Converte l'SVG in PNG
cairosvg.svg2png(url='chess_board.svg', write_to='chess_board.png')

# Leggi il PNG con OpenCV
img = cv2.imread('chess_board.png')

# Converti l'immagine da BGR a RGB
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Visualizza l'immagine con OpenCV
cv2.imshow('Chess Board', img_rgb)
cv2.waitKey(0)
cv2.destroyAllWindows()
