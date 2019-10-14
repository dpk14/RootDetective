import src.engine.functions.root_analyzer.main as main
from src.engine.functions.function import Function

class GetRootData(Function):

    def __init__(self, data_display):
        self.data_display = data_display

    def call(self, args):
        image_folder_path = args[0]
        output_path = args[1]
        self.data_display.clear()
        data = main.generate_data(image_folder_path, self.data_display.data_tracker)
        error_message = self.data_display.display_data(data)
        return ""

