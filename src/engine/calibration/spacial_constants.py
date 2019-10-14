import cv2
import src.tools.back_end.file_toolkit as tools
import numpy as np

BOX_HEIGHT_MM = 97
BOX_HEIGHT_TO_LIP_TOP_MM = 86
MAX = 255

def find_mm_per_pixel(img_path): #image should be of an empty bin
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    #img = cv2.GaussianBlur(img, (15, 15), 0)
    img = cv2.Sobel(img, ksize=3, ddepth=-1, dx=0, dy=1)
    retval, img = cv2.threshold(img, thresh=65, maxval=MAX,
                                 type=cv2.THRESH_BINARY)
    lines = cv2.HoughLinesP(img, 2, np.pi / 180, 3, minLineLength=300, maxLineGap=50)
    print(len(lines))
    highest_y = img.shape[0]
    max_line = lines[0]
    for line in lines:
        for x1, y1, x2, y2 in line:
            #cv2.line(img, (x1, y1), (x2, y2), 255, 10)
            y_avg = (y1 + y2) / 2
            if y_avg < highest_y:
                highest_y = y_avg
                max_line = line
    for x1, y1, x2, y2 in max_line:
        cv2.line(img, (x1, y1), (x2, y2), 255, 25)
    return BOX_HEIGHT_MM/y_avg