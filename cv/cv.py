import cv2

from chessboard.chessboard import getChessboardCorners
from chess_pieces.chess_pieces import getPiecesList

import numpy as np



def getCentersPerspectiveAdjusted(pieces, matrix):
	centers = []
	for i in range(len(pieces)):
		p = pieces[i]
		# Perspective warp the pieces' coordinates
		new_coord = cv2.perspectiveTransform(np.array([(p[1],p[2])], dtype=np.float32), matrix)
		new_coord = new_coord[0]
		

		# Calculate the center of the box (weighted towards the bottom, to make sure it falls in the cell)
		x = round((new_coord[0][0]+new_coord[1][0])/2)
		y = round((new_coord[0][1]*0.3+new_coord[1][1]*0.7))
		c = (x, y)
		
		centers.append((p[0], c))

	return centers


def getIndexes(centers):
	# List of ranges coords for every chell
	ranges = [[0, 80], [80, 160], [160, 240], [240, 320], [320, 400], [400, 480], [480, 560], [560, 640]]

	indexes = []
	for p in centers:
		for index, (start, end) in enumerate(ranges, start=1):
			# Check the x
			if p[1][0] in range(start, end + 1):
				i = index
			if p[1][1] in range(start, end + 1):
				j = index
		if p[1][0] < 0 or p[1][1] < 0:
			print("The piece: ", p, "is outside the chessboard")
		else:
			try:
				indexes.append((p[0], i, j))
			except:
				print("Can't position the piece :",p)
				continue

	return indexes

def getChessboardMatrix(indexes):
	chessboard = np.zeros((8, 8), dtype=str)
	chessboard[:] = ' '

	for p in indexes:
		i = p[1] - 1
		j = p[2] - 1
		if chessboard[j][i] != ' ':
			print(p, " is overwriting ", chessboard[j][i], " in ", i, j)
		chessboard[j][i] = p[0]

	return chessboard




def getFen(filename):
	chessboard = getChessboardCorners(filename)
	pieces = getPiecesList(filename)

	pts1 = np.float32(chessboard)
	pts2 = np.float32([[0,0], [0,640], [640,640], [640,0]])

	matrix = cv2.getPerspectiveTransform(pts1, pts2)

	# Find the center point for every piece's box, passing the perspective matrix
	centers = getCentersPerspectiveAdjusted(pieces, matrix)

	# Finding the indexes for every piece
	indexes = getIndexes(centers)

	# Creating a matrix that represents the chessboard
	board = getChessboardMatrix(indexes)

	fen = ""

	for l in board:
		i = 0
		while i < len(l):
			if l[i] == ' ':
				c = 1
				for j in range(i+1, len(l)):
					if l[j] == ' ':
						c += 1
					else:
						break
				fen += str(c)
				i += c-1
			else:
				fen += l[i]
			i += 1
		fen += '/'
	fen = fen[:-1]


	# To debug, it visualizes the images
	if __name__ == '__main__':
		img = cv2.imread(filename)
		img = cv2.resize(img, (640, 640))

		# Draw chessboard and pieces' box
		cv2.drawContours(img, [chessboard], -1, (0,0,255), 3)
		[cv2.rectangle(img, p[1], p[2], (0,255,0), 2) for p in pieces]

		# Perspective Warp the image
		pts1 = np.float32(chessboard)
		pts2 = np.float32([[0,0], [0,640], [640,640], [640,0]])

		matrix = cv2.getPerspectiveTransform(pts1, pts2)
		result = cv2.warpPerspective(img, matrix, (640, 640))

		[cv2.circle(result, c[1], 2, (255, 0, 0), -1) for c in centers]

		cv2.imshow("Risultato", result)

	return fen

if __name__ == '__main__':
	filename = 'test6.jpg'

	fen = getFen(filename)

	print(fen)
	cv2.waitKey()
