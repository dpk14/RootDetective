EMPTY_INPUT_FILENAME = "Must specify input filename"
EMPTY_OUTPUT_FILENAME = "Must specify output filename"
INCORRECT_NUM_BOXES = "Invalid number of boxes"
NONEMPTY_FOLDER_ERROR = "Output folder must be empty"
INCORRECT_INPUT_FILE_FORMAT = "Input file has incorrect format"

def validate_inputs(filename1, filename2, num_boxes, index):
    if len(filename1) == 0:
        return EMPTY_INPUT_FILENAME
    if len(filename2) == 0:
        return EMPTY_OUTPUT_FILENAME
    if index < 2:
        try:
            int(num_boxes)
            print("YE")
            if int(num_boxes) <= 0:
                return INCORRECT_NUM_BOXES
        except:
            return INCORRECT_NUM_BOXES
    return ""
