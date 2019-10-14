import os

from src.engine.functions.function import Function
from src.engine.functions.sorter import QR_handler, general_sorting
import src.tools.back_end.file_toolkit as tools

INTERMEDIATE_FILENAME = "intermediate"

class SortImgByQR(Function):

    def call(self, args):
        path_in = args[0]
        path_out = args[1]
        num_boxes = args[2]
        project_root = os.path.dirname(os.path.abspath(__file__))
        intermediate_directory = tools.make_path(project_root, INTERMEDIATE_FILENAME)
        os.mkdir(intermediate_directory)
        error_message = SortImgToFolders().call([path_in, intermediate_directory, num_boxes])
        if error_message is not "":
            return error_message
        error_message = QR_handler.sort_by_QR(path_in=intermediate_directory, path_out=path_out)
        os.remove(intermediate_directory)
        return error_message

class SortImgToFolders(Function):

    def call(self, args):
        print(args)
        path_in = args[0]
        path_out = args[1]
        num_boxes = args[2]
        tools.create_empty_output_folders(path_out=path_out, num_boxes=num_boxes)
        return general_sorting.copy_files_to_folders(path_in=path_in, path_out=path_out, num_boxes=num_boxes)

    def sort_folders_by_QR(self, path_in, path_out, make_sorted_directory=True):
        return QR_handler.sort_by_QR(path_in, path_out, make_sorted_directory)

class SortFoldersByQR(Function):

    def call(self, args):
        path_in = args[0]
        path_out = args[1]
        error_message = QR_handler.sort_by_QR(path_in, path_out)
        return error_message

class MergeData(Function):

    def call(self, args):
        secondary_data_path = args[0]
        main_data_path = args[1]
