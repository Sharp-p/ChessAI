from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import torch
import numpy as np
import cv2

def getPieces(result):
    # Get the boxes from the result
    boxes = result.boxes

    # Create pieces list
    pieces = []


    for box in boxes:
        b = box.xyxy[0] # get box coordinates in (left, top, right, bottom) format
        c = box.cls     # get box class

        # Get the two points
        p1 = (int(b[0].item()), int(b[1].item()))
        p2 = (int(b[2].item()), int(b[3].item()))

        # Match the class with the FEN notation
        match c:
            case 0:
                classe = "b"
            case 1:
                classe = "k"
            case 2:
                classe = "n"
            case 3:
                classe = "p"
            case 4:
                classe = "q"
            case 5:
                classe = "r"
            case 6:
                classe = "B"
            case 7:
                classe = "K"
            case 8:
                classe = "N"
            case 9:
                classe = "P"
            case 10:
                classe = "Q"
            case 11:
                classe = "R"

        pieces.append((classe, p1, p2))


    return pieces

def getPiecesList(filename):
    # Load the model
    model = YOLO("chess_pieces.pt")

    # Preprocess the image
    img = cv2.imread(filename)
    img = cv2.resize(img, (640, 640))

    # Load the file and do inference
    results = model(img, save=True, save_conf=True, conf=0.5)


    # Convert pieces found into list as (class, (x1,y1), (x2,y2))
    pieces = getPieces(results[0])

    return pieces


if __name__ == "__main__":
    filename = "test.jpg"
    img = cv2.imread(filename)
    img = cv2.resize(img, (640, 640))

    pieces = getPiecesList(filename)

    [cv2.rectangle(img, p[1], p[2], (0,255,0), 2) for p in pieces]

    cv2.imshow("Pezzi", img)
    cv2.waitKey()


