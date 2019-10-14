import cv2
import os, os.path
from src.tools.back_end import error_checker
from src.engine.functions.sorter import QR_read
import numpy as np
import shutil
import statistics as stats
import src.tools.back_end.file_toolkit as tools

X_TOP_CROP = 250
X_BOTTOM_CROP = 250
Y_TOP_CROP = 200
Y_BOTTOM_CROP = 400
MIDDLE_STRIP_CLIP_PERCENTAGE = .4
BLACK_THRESHOLD = 60
EMPTY_PERCENTAGE = .9     #Percentage of black pixels required to determine an image empty
SAMPLE_SIZE = 15
PIXEL_MAX = 255
SCREEN_DIMENSIONS = "1000x500"

DEFAULT_BASE_FOLDER_PATH = r"C:\Users\dpk14\Dropbox"
DEFAULT_INPUT_FOLDER_NAME = "5_24_19_sorted"
DEFAULT_OUTPUT_FOLDER_NAME = "5_24_19_sorted_by_QR"

QR_RANDOMIZER_MAX = 20000

def find_middle_strip(image):
    shape = image.shape
    rows = shape[0]
    middle_strip = tools.crop(image, x_bottom_crop=int(rows * MIDDLE_STRIP_CLIP_PERCENTAGE),
                             x_top_crop=int(rows - (rows * MIDDLE_STRIP_CLIP_PERCENTAGE)), y_bottom_crop=0,
                             y_top_crop=0)
    return middle_strip

def get_folder_QR(filenames, folder_filepath, num_folders, folder_name, folder_index):
    QR_codes = []
    num_files = len(filenames)
    taken = []
    empty_count = 0
    for i in range(SAMPLE_SIZE):
        rand_index = 0
        while rand_index in taken:
            rand_index = int(np.random.uniform(num_files - 1))
        taken.append(rand_index)
        image_name = filenames[rand_index]
        image_filepath = tools.make_path(directory_path=folder_filepath, name=image_name)
        image = cv2.imread(filename=image_filepath, flags=cv2.IMREAD_GRAYSCALE)
        cropped_image = tools.crop(image=image, x_top_crop=X_TOP_CROP, y_top_crop=Y_TOP_CROP,
                                  x_bottom_crop=X_BOTTOM_CROP,
                                  y_bottom_crop=Y_BOTTOM_CROP)
        retval, cropped_image = cv2.threshold(cropped_image, thresh=BLACK_THRESHOLD, maxval=PIXEL_MAX,
                                              type=cv2.THRESH_BINARY)
        try:
            code = QR_read.read_barcode(img=cropped_image)
            QR_codes.append(code)
            # print("YEET: QR code of image " + image_name + " in " + folder_name + " displaying")
        except:
            middle_strip = find_middle_strip(image)
            if tools.is_blank(middle_strip):
                empty_count+=1
            else:
                # print("ERROR: QR code of image " + image_name + " (image index " + str(
                #    rand_index) + ") in " + folder_name +
                #      " (folder index " + str(folder_index) + ") not displaying")
                rand_code = np.random.uniform(num_folders, num_folders + QR_RANDOMIZER_MAX)
                while rand_code in QR_codes:
                    rand_code = np.random.uniform(num_folders, num_folders + QR_RANDOMIZER_MAX)
                QR_codes.append(int(rand_code))
    if empty_count == SAMPLE_SIZE:
        return None
    try:
        QR_code = stats.mode(QR_codes)
        print("Folder number " + str(folder_name) + " has QR code " + str(QR_code))
        return QR_code
    except:
        rand_index = int(np.random.uniform(0, len(QR_codes) - 1))
        QR_code = QR_codes[rand_index]
        print("Folder number " + str(folder_name) + " is faulty and has been given random QR_code " + str(QR_code))
        return QR_code


def display_image_by_index(self, input_path, folder_index, image_index=0):
    folders = os.listdir(input_path)
    folder_name = folders[folder_index]
    image_folder_filepath = tools.make_path(directory_path=input_path, name=folder_name)
    filenames = os.listdir(image_folder_filepath)
    image_name = filenames[image_index]
    image_filepath = tools.make_path(directory_path=image_folder_filepath, name=image_name)
    image = cv2.imread(filename=image_filepath, flags=cv2.IMREAD_GRAYSCALE)
    cropped_image = tools.crop(image=image, x_top_crop=X_TOP_CROP, y_top_crop=Y_TOP_CROP, x_bottom_crop=X_BOTTOM_CROP,
                         y_bottom_crop=Y_BOTTOM_CROP)

def sort_by_QR(self, input_path, output_path, make_sorted_directory=True):

    if len(os.listdir(output_path)) > 0:
        return error_checker.NONEMPTY_FOLDER_ERROR

    image_folders = os.listdir(input_path)
    num_folders = len(image_folders)

    for index in range(num_folders):
        image_folder_name = image_folders[index]
        image_folder_path = tools.make_path(directory_path=input_path, name=image_folder_name)
        list_of_image_filenames = os.listdir(image_folder_path)
        sorted_filename = get_folder_QR(filenames=list_of_image_filenames,
                                                 folder_filepath=image_folder_path,
                                                 num_folders=num_folders, folder_name=image_folder_name, folder_index=index)

        if sorted_filename == None:
            print("Folder number " + image_folder_name + " is Empty")
        elif make_sorted_directory:
            output_path = tools.make_path(output_path, sorted_filename)
            shutil.copytree(image_folder_path, output_path)
        else:
            continue
    return ""