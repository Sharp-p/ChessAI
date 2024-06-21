#### Evaluation:
*Cosa è*:
- Un valore che indica quanto è buona una posizione dal punto di vista del bianco, questo valore è misurato usando il [valore delle pedine](https://www.chess.com/terms/chess-piece-value), la posizione e mosse future.
*Come si ottiene:*
- Usando la Eval Function.
#### Eval Function:
*Cosa è*:
- Una rete neurale (in passato algoritmi appositi), che prende in input una posizione e ritorna l'evaluation.
*Output*:
- Float
*Input*:
- Stringa da 808 bits, che definiscono:
	1. **Board**: usiamo per ogni tipo di tipo di pedina una [bitboard](https://www.chessprogramming.org/Bitboards)(da 64 bits).
	2. **Indice di mossa**.
	3. **Colore in cui muoversi**.
	4. **En passant**. Sulle strisce pedonali prendi il pedone



# COSE DA FARE:
1. Come prendere testo in file compresso, o come decomprimere file compresso da 30GB 		[FATTO]
2. Leggere ogni mossa di ogni partita, pur che sia valida									[FATTO] 	
3. Trasformare il FEN in binario															[FATTO]
5. Eliminare il vecchio db/Fare nuovo db ChessMatches con tabella Matches con attributi:
	- ID mossa
	- FEN
	- Binario (codifica FEN)
	- Eval
6. Scrivere il codice per popolare il DB
7. Capire come funziona Collab
8. Popolare il DB