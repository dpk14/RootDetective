import threading

import cv2

import src.tools.back_end.file_toolkit as tools

START_IN_HOURS = 24
MINUTES_PER_IMAGE = 15
IMAGES_PER_HOUR = 60 / MINUTES_PER_IMAGE

class Root:
    def __init__(self, image, start_index, end_index, exists=True):
        try:
            self.image = image.image
        except:
            self.image = image
        num_images_bw_indices = end_index - start_index
        hrs = num_images_bw_indices/IMAGES_PER_HOUR
        height = image.shape[0]
        self.hrs_per_pixel = hrs/height
        self.exists = exists

class Rectangle:
    def __init__(self, x, y, w, h):
        self.x=x
        self.y=y
        self.width=w
        self.height=h

'''
the root analyzer scripts carry around a DataTracker instance. If an image analysis method produces an image that should be visible to the user, 
the data is set to the tracker. A thread in the controller sees that the data has been updated, and displays the updated data
'''
import threading


class DataTracker:
    def __init__(self, filename=None, caption=None):
        self.filename = filename
        self.caption = caption
        self.data_updated = False
        self.continue_analysis = threading.Event()

    def save_and_show(self, image, filename, caption=""):
        filepath = tools.make_path(tools.SORTING_FOLDER_PATH, filename)
        cv2.imwrite(filename=filepath, img=image)
        self.set_data(filename=filepath, caption=caption)

    def set_data(self, filename, caption=""):
        self.filename = filename
        self.caption = caption
        self.data_updated = True
        self.pause_analysis()

    def pause_analysis(self):
        self.continue_analysis.wait()
        self.continue_analysis.clear()