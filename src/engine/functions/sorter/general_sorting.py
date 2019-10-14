#!/usr/bin/env python
# coding: utf-8

import os
from os import listdir
from os.path import isfile, join
from shutil import copyfile
import shutil
import subprocess
import src.tools.back_end.file_toolkit as tools

#set various paths
#where images are
from src.tools.back_end import error_checker

INTERMEDIATE_FILENAME = "intermediate"

DEFAULT_PATH_IN=r"D:\images\5_24_19\\"

#mypathout is the directory where the images will go
DEFAULT_PATH_OUT=r"D:\images\5_24_19_sorted"

#number of boxes in this experiment.
DEFAULT_NUM_BOXES=17

#this will make a number of directories in the outdirectory equal to the number of boxes, names 1\, 2\, 3\, etc

def copy_files_to_folders(path_in, path_out, num_boxes):
    #create onlyfiles w column list with file name in first column and parsed image # as second column
    onlyfiles = [f for f in listdir(path_in) if isfile(join(path_in, f))]
    # some code just to see what's in the lists
    # print(onlyfiles[0])
    # print(files[0][1])
    # flycap names images with a _####, from 0000 to 9999, then goes to 10000,
    print(onlyfiles[0])
    try:
        filenum = [int(c.rsplit('-', 1)[1].rsplit('.', 1)[0]) for c in onlyfiles]
    except:
        return error_checker.INCORRECT_INPUT_FILE_FORMAT
    # final list
    files = list(zip(onlyfiles, filenum))
    files = sorted(files, key=lambda l: l[1], reverse=False)
    count = 0
    for z in range(1,len(files),num_boxes):
        count = count +1
        for y in range(num_boxes):
            savefile=path_out+"\\"+str(y+1)+"\\"+str(100000000 + count)[-8:] + ".png"
            filename=path_in+"\\"+ files[z+y-1][0]
            copyfile(filename, savefile)
    return ""

# This will make the timelapse images
def make_time_lapse(path_out):
    # os.mkdir(mypathout+"\\videos")
    contents = os.listdir(path_out)
    for z in contents[0:84]:
        print(z)
        os.chdir(path_out + "\\" + z)
        # print(os.getcwd())
        subprocess.call(
            "C:/Users/iwt/ffmpeg/bin/ffmpeg.exe -framerate 15 -i %08d.png -c:v libx264 -r 20 -pix_fmt yuv420p outfile.mp4")

        outfile = path_out + "\\videos\\" + z + ".mp4"
        # print(outfile)
        os.rename("outfile.mp4", outfile)
    # outfile= outdir + "\\" + str(y+1) + ".mp4"
    # subprocess.call("ffmpeg.exe -framerate 15 -i %08d.png -c:v libx264 -r 20 -pix_fmt yuv420p outfile.mp4")


def make_filename(file_number):
    MAX_LENGTH = 8
    length = len(str(file_number))
    number_len = length
    header = ""
    zero_count = 0
    while zero_count < MAX_LENGTH - number_len:
        header+="0"
        zero_count+=1
    filename = header + str(file_number) + ".png"
    return filename

def combine(self, secondary_data_path, main_data_path):
    main_files = os.listdir(main_data_path)
    secondary_files = os.listdir(secondary_data_path)
    new_start = len(main_files) + 1
    num_of_new_files = len(secondary_files)

    for index in range(num_of_new_files):
        old_filename = secondary_files[index]
        old_filepath = tools.make_path(secondary_data_path, old_filename)
        new_filename = make_filename(index + new_start)
        new_filepath = tools.make_path(main_data_path, new_filename)
        shutil.copyfile(old_filepath, new_filepath)

def merge_data(main_data_path, secondary_data_path):
    main_image_folders = os.listdir(main_data_path)
    secondary_image_folders = os.listdir(secondary_data_path)
    num_of_main_image_folders = len(main_image_folders)
    num_of_secondary_image_folders = len(secondary_image_folders)
    for folder_index_secondary in range(num_of_secondary_image_folders):
        folder_name_secondary = secondary_image_folders[folder_index_secondary]
        folder_path_secondary = tools.make_path(secondary_data_path, folder_name_secondary)
        share_name = False
        for folder_index_main in range(num_of_main_image_folders):
            folder_name_main = main_image_folders[folder_index_main]
            folder_path_main = tools.make_path(main_data_path, folder_name_main)
            if folder_name_main == folder_name_secondary:
                share_name = True
                combine(secondary_data_path=folder_path_secondary, main_data_path=folder_path_main)
        if not share_name:
            new_path = tools.make_path(main_data_path, folder_name_secondary)
            shutil.copytree(folder_path_secondary, new_path)
    return ""
