import tkinter as tk
import ttkthemes

from src.user_interface import configurations as config
from src.user_interface.main_display import Selector
import src.user_interface.main_display as display

def run():
    root = tk.Tk()
    root.title(config.WINDOW_TITLE)
    root.style=ttkthemes.ThemedStyle()
    root.style.theme_use("equilux")
    root.geometry(display.SCREEN_DIMENSIONS)
    selector = Selector(root)
    root.mainloop()

run()
