import os
from src.engine.functions.root_analyzer import filtering, data_manager
import src.engine.functions.root_analyzer.detector as detector
import src.tools.back_end.file_toolkit as tools
from src.user_interface import plotter

CURRENT_PATH = os.path.abspath(__file__)
PARENT_PATH = os.path.abspath(os.path.join(CURRENT_PATH, os.pardir))
DATA_MANAGER_PATH = os.path.abspath(os.path.join(PARENT_PATH, os.pardir))

MAX_INTENSITY_PROJ_FILENAME = "max_intensity.jpg"
SORTING_FOLDER_NAME = "data"
SORTING_FOLDER_PATH = tools.make_path(DATA_MANAGER_PATH, SORTING_FOLDER_NAME)
MAX_INTENSITY_PROJ_FILENAME = "max_intensity.jpg"
LINES_FILENAME = "lines.jpg"
LINES_FILEPATH = tools.make_path(SORTING_FOLDER_PATH, LINES_FILENAME)
SEEDS_FILENAME = "seeds.jpg"
SEEDS_FILEPATH = tools.make_path(SORTING_FOLDER_PATH, SEEDS_FILENAME)


def generate_data(image_folder_path, data_tracker):
    filterer = filtering.Filterer(data_tracker)
    detec = detector.Detector(data_tracker)

    max_int_proj_filepath = tools.make_path(SORTING_FOLDER_PATH, MAX_INTENSITY_PROJ_FILENAME)
    filterer.generate_max_intensity_proj(image_folder_path=image_folder_path, output_path=max_int_proj_filepath)
    initial_crop, water, root_images = detec.locate_interest_regions(max_int_proj_filepath)
    roots = filterer.trim_for_data_capture(initial_crop, water, root_images, image_folder_path)
    data_packages = {}
    for root_num in roots.keys():
        root = roots[root_num]
        if root.exists:
            data = filterer.convert_to_data(root.image)
            curve_pair = data_manager.find_root_curves(data, root.hrs_per_pixel)
        else:
            curve_pair = data_manager.no_root()
        additional_stats = data_manager.generate_additional_stats(curve_pair)
        data_packages[root_num] = data_manager.DataPackage(curve_pair, additional_stats)
    #plotter.graph_curves(all_curves)
    return data_packages


