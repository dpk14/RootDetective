import os
import sys

import cv2
from natsort import natsort
from src.engine.functions.data import config

BLACK_THRESHOLD = 80
PIXEL_MAX = 255
EMPTY_PERCENTAGE = .99
BLUR_KERNEL = (7, 7)
SORTING_FOLDER_PATH = config.DIRECTORY_PATH

def make_path(directory_path, name):
    return directory_path + "\\" + str(name)


def show_image(img, winname=""):
    cv2.imshow(winname=winname, mat=img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def num_images(path):
    return len(os.listdir(path))

def is_blank(image, threshhold = BLACK_THRESHOLD, percentage=EMPTY_PERCENTAGE):
    shape = image.shape
    rows = shape[0]
    cols = shape[1]
    area = cols*rows
    image = cv2.GaussianBlur(image, BLUR_KERNEL, 0)
    retval, image = cv2.threshold(image, thresh=threshhold, maxval=PIXEL_MAX,
                  type=cv2.THRESH_BINARY_INV)
    return cv2.countNonZero(image) >= percentage * area

def find_image_at_index(index, path):
    image_names = os.listdir(path)
    natsort.natsorted(image_names, reverse=False)
    image_name = image_names[index]
    image_path = make_path(path, image_name)
    return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

def create_empty_output_folders(num_boxes, path_out):
    for x in range(num_boxes):
        os.mkdir(path_out+"\\"+str(x+1))