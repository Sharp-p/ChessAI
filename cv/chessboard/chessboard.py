from ultralytics import YOLO
import torch
import numpy as np
import cv2



def getMask(model, result):
    # get array results
    masks = result.masks.data
    boxes = result.boxes.data
    # extract classes
    clss = boxes[:, 5]
    # get indices of results where class is 0 (chessboard has class 0)
    chessboard_indices = torch.where(clss == 0)
    # use these indices to extract the relevant masks
    chessboard_masks = masks[chessboard_indices]
    # scale for visualizing results
    chessboard_mask = torch.any(chessboard_masks, dim=0).int() * 255
    # save to file
    cv2.imwrite(str(model.predictor.save_dir / 'merged_segs.jpg'), chessboard_mask.cpu().numpy())

    mask = cv2.imread(str(model.predictor.save_dir / 'merged_segs.jpg'))
    mask = cv2.resize(mask, (640, 640))

    return mask

def sortPoints(approx):
    somme = []

    # Find the UpperLeft and DownRight points
    for i in range(len(approx)):
        num = approx[i][0]
        somme.append(num[0] + num[1])

    # Put the UpperLeft point in first position and DownRight point in third position
    ul = np.argmin(somme)
    dr = np.argmax(somme)
    approx[[ul, 0]] = approx[[0, ul]]
    approx[[dr, 2]] = approx[[2, dr]]


    if approx[1][0][0] > approx[3][0][0]:
        approx[[1, 3]] = approx[[3, 1]]


    return approx



def getChessboardCorners(filename):
    # Load the model
    model = YOLO("chessboard.pt")

    # Preprocess the image
    img = cv2.imread(filename)
    img = cv2.resize(img, (640, 640))
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(imgray, (5,5))
    img = cv2.cvtColor(blur, cv2.COLOR_GRAY2BGR)

    # Load the file and do inference
    results = model(img, save=True, save_conf=True, conf=0.5)

    # Extract binary mask for the chessboard
    # --------------------------------------------------------------------------------------------------
    mask = getMask(model, results[0])


    # Extract contours
    # --------------------------------------------------------------------------------------------------
    imgray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)

    # Take only the largest contour (to avoid errors)
    contour = max(contours, key = cv2.contourArea)
    
    # Draw approximated polygon for the chessboard
    # --------------------------------------------------------------------------------------------------
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.05 * perimeter, True)

    points = sortPoints(approx)

    return approx

if __name__ == "__main__":
    filename = "test4.jpg"
    img = cv2.imread(filename)
    img = cv2.resize(img, (640, 640))

    approx = getChessboardCorners(filename)
    
    cv2.drawContours(img, [approx], -1, (0,0,255), 3)

    cv2.imshow('Contours', img)
    cv2.waitKey(0)

