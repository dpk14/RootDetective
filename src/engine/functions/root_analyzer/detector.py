import os
import cv2
import natsort as natsort
import numpy as np
import src.tools.back_end.file_toolkit as tools
from src.tools.back_end import cropper, models

X_TOP_CROP = 300
X_BOTTOM_CROP = 450
Y_TOP_CROP = 450
Y_BOTTOM_CROP = 0
SEED_THRESHOLD = 100
ROOT_THRESHOLD = 70
MAX = 255
SAFETY_OFFSET_WATERLINE = 30
SAFETY_OFFSET_FROM_SEED = 4
SAFETY_OFFSET_ROOTS = 10

CURRENT_PATH = os.path.abspath(__file__)
PARENT_PATH = os.path.abspath(os.path.join(CURRENT_PATH, os.pardir))
DATA_MANAGER_PATH = os.path.abspath(os.path.join(PARENT_PATH, os.pardir))

SORTING_FOLDER_NAME = "data"
SORTING_FOLDER_PATH = tools.make_path(DATA_MANAGER_PATH, SORTING_FOLDER_NAME)
LINES_FILENAME = "lines.jpg"
LINES_FILEPATH = tools.make_path(SORTING_FOLDER_PATH, LINES_FILENAME)
SEEDS_FILENAME = "seeds.jpg"
SEEDS_FILEPATH = tools.make_path(SORTING_FOLDER_PATH, SEEDS_FILENAME)

HORIZ_DETECTOR_BLUR_KERNEL = (21, 21)
VERTICAL_DETECTOR_BLUR_KERNEL = (51, 51)
SEED_LOCATION_BLUR_KERNEL = (55, 55)
SEED_MIN_AREA = 1500
SEED_MAX_AREA = 8000
ROOT_IMAGE_WIDTH = 100

class Detector:

    def __init__(self, data_tracker):
        self.data_tracker = data_tracker

    def locate_water(self, image):
        shape = image.shape
        height = shape[0]
        vertical_midpoint = height/2

        blurred = cv2.GaussianBlur(image, (21, 21), 0)
        retval, threshed = cv2.threshold(blurred, 200, MAX, type=cv2.THRESH_BINARY)
        horiz_edges = cv2.Sobel(threshed, ksize=5, ddepth=-1, dx=0, dy=1)
        lines = cv2.HoughLinesP(horiz_edges, 2, np.pi / 180,  3, minLineLength=90, maxLineGap=20)

        top_line_y_max = 0
        bottom_line_y_min = height

        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(horiz_edges, (x1, y1), (x2, y2), 255, 10)
                y_avg = (y1 + y2) / 2
                if y_avg < vertical_midpoint:
                    top_line_y_max=max(top_line_y_max, y_avg)
                else:
                    bottom_line_y_min=min(bottom_line_y_min, y_avg)

        crop_from_top = int(top_line_y_max) + SAFETY_OFFSET_WATERLINE
        crop_from_bottom = height - (int(bottom_line_y_min) - SAFETY_OFFSET_WATERLINE)

        water = cropper.crop(image, y_top_crop=crop_from_top, y_bottom_crop=crop_from_bottom)
        cv2.imwrite(LINES_FILEPATH, water.image)
        self.data_tracker.save_and_show(image=water.image, filename="water.jpg",
                                        caption="Water surrounding the roots")
        return water

    def locate_roots(self, water, seed_borders):
        root_images = {}
        for key in seed_borders.keys():
            seed = seed_borders[key]
            crop_from_left = seed.x - int(ROOT_IMAGE_WIDTH / 2)
            crop_from_right = water.shape[1] - (seed.x + int(ROOT_IMAGE_WIDTH / 2))
            seed_base = seed.y+seed.height + SAFETY_OFFSET_FROM_SEED
            root_image = cropper.crop(water, x_bottom_crop=crop_from_left, x_top_crop=crop_from_right, y_top_crop=seed_base)
            root_images[key] = root_image
            self.data_tracker.save_and_show(image=root_image.image, filename="root_" + str(key) + ".jpg",
                                            caption="Root " + str(key))
        return root_images

    def find_seeds(self, image):
        blurred = cv2.GaussianBlur(image, (41, 41), 0)
        retval, threshed = cv2.threshold(blurred, SEED_THRESHOLD, MAX, type=cv2.THRESH_BINARY)
        seeds, hier = cv2.findContours(threshed, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        root_count = 0
        seed_borders = {}
        for index in range(len(seeds)):
            seed = seeds[index]
            x, y, w, h = cv2.boundingRect(seed)
            area = w * h
            if (SEED_MIN_AREA < area < SEED_MAX_AREA) and (SEED_MIN_AREA < cv2.contourArea(seed) < SEED_MAX_AREA):
                cv2.rectangle(image, (x, y), (x+w, y+h), 0)
                seed_border = models.Rectangle(x, y, w, h)
                root_count+=1
                seed_borders[root_count] = seed_border
        self.data_tracker.save_and_show(image=image, filename="seeds.jpg",
                                        caption="Binding contours of seeds")
        return seed_borders

    def find_sprout_index(self, interest_region, image_folder_path):
        image_names = os.listdir(image_folder_path)
        natsort.natsorted(image_names, reverse=False)
        for index in range(len(image_names)):
            name = image_names[index]
            path = tools.make_path(image_folder_path, name)
            image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            region = cropper.crop(image, crop=interest_region).image
            just_below_seed = cropper.crop(region, y_bottom_crop=int(.95 * region.shape[0])).image
            if not tools.is_blank(just_below_seed, percentage = .99):
                return index
        return 0

    def locate_interest_regions(self, max_int_proj_filepath):
        max_proj = cv2.imread(max_int_proj_filepath, cv2.IMREAD_GRAYSCALE)
        initial_crop = cropper.crop(max_proj, x_bottom_crop=X_BOTTOM_CROP, y_bottom_crop=Y_BOTTOM_CROP,
                                    x_top_crop=X_TOP_CROP, y_top_crop=Y_TOP_CROP)
        water = self.locate_water(initial_crop.image)
        seed_borders = self.find_seeds(water.image)
        roots = self.locate_roots(water.image, seed_borders)
        return initial_crop, water, roots

    def get_contour_info(self, root):
        contours, hier = cv2.findContours(root, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        max_area = 0
        max_index = 0
        junk_contours = []
        for index in range(len(contours)):
            contour = contours[index]
            #cv2.drawContours(root, [contour], 0, 0, -1)
            x, y, w, h = cv2.boundingRect(contour)
            #cv2.rectangle(root, (x, y), (x + w, y + h), 255)
            area = w * h
            if y > 0 or (y == 0 and x == 0):
                cv2.fillPoly(root, pts=[contour], color=0)
                junk_contours.append(contour)
            elif area > max_area:
                max_area = area
                max_index = index
        root_contour = contours[max_index]
        return root_contour, junk_contours

    def find_root_tip(self, root, show=False):
        root = cv2.GaussianBlur(root, (11, 11), 0)
        root = cv2.Sobel(root, ksize=5, ddepth=-1, dx=1, dy=0)
        retval, root = cv2.threshold(root, thresh=65, maxval=MAX,
                                     type=cv2.THRESH_BINARY)
        root_contour, junk_contours = self.get_contour_info(root)
        x, y, w, h = cv2.boundingRect(root_contour)
        location = h + y
        return location

    def remove_contours(self, image, junk_contours):
        for contour in junk_contours:
            cv2.fillPoly(image, pts=[contour], color=0)
        return image
