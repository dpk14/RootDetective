class CroppableImage:
    def __init__(self, image, parent_image, x_base_crop=0, x_top_crop=0, y_base_crop=0, y_top_crop=0):
        self.x_base_crop = x_base_crop
        self.x_top_crop = x_top_crop
        self.y_base_crop = y_base_crop
        self.y_top_crop = y_top_crop
        self.image = image
        self.parent_image = parent_image
        self.shape = image.shape

class CropStruct:
    def __init__(self, x_base_crop=0, x_top_crop=0, y_base_crop=0, y_top_crop=0):
        self.x_base_crop = x_base_crop
        self.x_top_crop = x_top_crop
        self.y_base_crop = y_base_crop
        self.y_top_crop = y_top_crop

def crop(parent_image, x_top_crop=0, x_bottom_crop=0, y_bottom_crop=0, y_top_crop=0, crop=None):
    try:
        image = parent_image.image
        shape = image.shape
    except:
        shape = parent_image.shape
        image = parent_image
    height = shape[0]
    width = shape[1]
    if crop is not None:
        x_top_crop = crop.x_top_crop
        x_bottom_crop = crop.x_base_crop
        y_top_crop = crop.y_top_crop
        y_bottom_crop = crop.y_base_crop
    cropped_image = image[y_top_crop: height - y_bottom_crop, x_bottom_crop: width - x_top_crop]
    return CroppableImage(image=cropped_image, parent_image=image, x_base_crop=x_bottom_crop, x_top_crop=x_top_crop,
                        y_base_crop=y_bottom_crop, y_top_crop=y_top_crop)

def find_crop_from_original(image, parents):
    x_top_crop = image.x_top_crop
    x_base_crop = image.x_base_crop
    y_top_crop = image.y_top_crop
    y_base_crop = image.y_base_crop

    for parent in parents:
        x_top_crop += parent.x_top_crop
        x_base_crop += parent.x_base_crop
        y_top_crop += parent.y_top_crop
        y_base_crop += parent.y_base_crop

    return CropStruct(x_base_crop=x_base_crop, x_top_crop=x_top_crop, y_top_crop=y_top_crop,
                      y_base_crop=y_base_crop)