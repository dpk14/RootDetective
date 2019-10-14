from src.engine.calibration import spacial_constants

PATH = r"C:\Users\dpk14\Downloads\box.png"

print(spacial_constants.find_mm_per_pixel(PATH))