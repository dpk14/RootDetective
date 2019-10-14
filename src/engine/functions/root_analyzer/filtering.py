import os

import cv2
from natsort import natsort

from src.engine.functions.root_analyzer.detector import Detector
from src.tools.back_end import file_toolkit as tools, cropper, models
import numpy as np

MINUTES_PER_IMAGE = 15
IMAGES_PER_HOUR = 60/MINUTES_PER_IMAGE
IMGS_IN_24_HRS = int(IMAGES_PER_HOUR*24)
MAX_IMAGES = IMGS_IN_24_HRS*2

CURRENT_PATH = os.path.abspath(__file__)
PARENT_PATH = os.path.abspath(os.path.join(CURRENT_PATH, os.pardir))
FUNCTION_PATH = os.path.abspath(os.path.join(PARENT_PATH, os.pardir))

MAX_INTENSITY_PROJ_FILENAME = "max_intensity.jpg"
SORTING_FOLDER_NAME = "data"
SORTING_FOLDER_PATH = tools.make_path(FUNCTION_PATH, SORTING_FOLDER_NAME)

MAX = 255

class Filterer:

    def __init__(self, data_tracker):
        self.data_tracker = data_tracker
        self.detector = Detector(data_tracker)

    def convert_to_data(self, image):
        retval, image = cv2.threshold(image, 80, MAX, type=cv2.THRESH_BINARY)
        root_contour, junk_contours = self.detector.get_contour_info(image)
        image = self.detector.remove_contours(image, junk_contours)
        return image

    def trim_for_data_capture(self, initial_crop, water, roots, image_folder_path):
        end_index = len(os.listdir(image_folder_path))
        parents = (initial_crop, water)
        for key in roots.keys():
            root = roots[key]
            if tools.is_blank(root.image): #seed hasn't germinated
                num_images = tools.num_images(image_folder_path)
                root = models.Root(root, start_index=0, end_index=num_images - 1, exists=False)
                roots[key] = root
            else:
                interest_region = cropper.find_crop_from_original(image=root, parents=parents)
                starting_index = self.detector.find_sprout_index(interest_region=interest_region, image_folder_path=image_folder_path) + IMGS_IN_24_HRS
                root_24_hrs_after_sprout = tools.find_image_at_index(starting_index, image_folder_path)
                root_24_hrs_after_sprout = cropper.crop(root_24_hrs_after_sprout, crop=interest_region).image
                starting_height = self.detector.find_root_tip(root_24_hrs_after_sprout)
                max_index = starting_index + MAX_IMAGES
                if max_index < end_index:
                    img = tools.find_image_at_index(max_index, image_folder_path)
                    img = cropper.crop(img, crop=interest_region).image
                    end_height = self.detector.find_root_tip(img)
                else:
                    end_height = self.detector.find_root_tip(root.image)
                trimmed = cropper.crop(root, y_bottom_crop=root.shape[0] - end_height, y_top_crop=starting_height)
                self.data_tracker.save_and_show(image=trimmed.image, filename="root_" + str(key) + "_interest_window.jpg",
                                    caption="Root " + str(key) + " interest window")
                root = models.Root(trimmed, starting_index, end_index)
                roots[key] = root
        return roots

    def generate_max_intensity_proj(self, image_folder_path, output_path):
        files = os.listdir(image_folder_path)
        natsort.natsorted(files, reverse=False)
        first_iteration = True
        max_index = len(files)
        for index in range(max_index):
            file = files[index]
            filepath = tools.make_path(image_folder_path, file)
            current_image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            if first_iteration:
                max_projection = current_image
                first_iteration = False
            else:
                max_projection=np.maximum(max_projection, current_image)
        self.data_tracker.save_and_show(image=max_projection, filename=MAX_INTENSITY_PROJ_FILENAME,
                                        caption="Max intensity projection")
        return max_projection