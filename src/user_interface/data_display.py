import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Separator

from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import src.tools.display.display_tools as tools
from src.tools.back_end.models import DataTracker
from src.user_interface import configurations as config

from src.user_interface import plotter

DELAY = 1
IMG_HEIGHT = 250

class DataDisplay:

    def __init__(self, root, win):
        self.root = root
        self.root.after(DELAY, self.check_data_tracker)
        self.frame = ttk.LabelFrame(win, text="Data", labelanchor=tk.N, style=config.LABEL_FRAME_STYLE)
        self.frame.configure(height=375, width=800)
        self.data_tracker = DataTracker()

    def pack(self, side=tk.TOP):
        self.frame.pack(side=side)

    def display_data(self, data):
        self.root.after(DELAY, lambda dat = data: self.make_tabs(data))
        return ""

    def make_tabs(self, data):
        notebook = ttk.Notebook(self.frame)
        self.display_curves(notebook, data)
        self.display_additional_stats(notebook, data)
        notebook.pack()

    def display_curves(self, notebook, data):
        for root_num in data.keys():
            tab = ttk.Frame(self.frame)
            tab.pack(expand=tk.FALSE)
            notebook.add(tab, text='Root Number ' + str(root_num))

            curve_pair = data[root_num].curve_pair
            fig = plotter.graph_curve_pair(curve_pair, root_num=str(root_num))
            canvas = FigureCanvasTkAgg(fig, tab)
            canvas.get_tk_widget().pack()
            canvas.draw()

    def display_additional_stats(self, notebook, data):
        tab = ttk.Frame(self.frame)
        tab.pack(expand=tk.FALSE)
        notebook.add(tab, text='Stats')
        for root_num in data.keys():
            root_frame = ttk.Frame(tab)
            root_frame.pack(side=tk.LEFT)
            stats = data[root_num].additional_stats
            if stats.germinated:
                germinated = "YES"
            else:
                germinated = "NO"
            ttk.Label(root_frame, text="Root " + str(root_num) + ":").pack(side=tk.TOP)
            ttk.Label(root_frame, text="Germinated: " + germinated).pack(side=tk.TOP)
            ttk.Label(root_frame, text="Average amplitude: " + str(stats.average_amplitude)).pack(side=tk.TOP)
            tools.pack_blank_col(tab, cols=2)


    def pause_and_display_progress_data(self, filename, caption):
            sub_frame = ttk.Frame(self.frame)
            sub_frame.pack(side=tk.TOP, fill=tk.BOTH)
            tools.pack_blank_row(sub_frame)
            label = ttk.Label(sub_frame, text=caption, font=config.MAIN_FONT, foreground=config.TEXT_COLOR)
            label.pack(side=tk.TOP)
            tools.pack_blank_row(sub_frame)
            image = Image.open(filename)
            ratio = image.width/image.height
            new_width = int(IMG_HEIGHT * ratio)
            image = image.resize((new_width, IMG_HEIGHT))
            image = ImageTk.PhotoImage(image)
            label = ttk.Label(sub_frame, image=image, font=config.MAIN_FONT, foreground=config.TEXT_COLOR)
            label.image = image
            label.pack(side=tk.TOP, fill=tk.BOTH)
            tools.pack_blank_row(sub_frame)
            button = ttk.Button(sub_frame, text="Continue analysis", command=lambda args=None: self.unpause(args), style=config.BUTTON_STYLE)
            button.pack(side=tk.TOP)
            tools.pack_blank_row(sub_frame)

    def unpause(self, args):
        self.data_tracker.continue_analysis.set()
        self.clear()

    def check_data_tracker(self):
        if self.data_tracker.data_updated:
            self.pause_and_display_progress_data(self.data_tracker.filename, self.data_tracker.caption)
            self.data_tracker.data_updated = False
        self.root.after(DELAY, self.check_data_tracker)

    def clear(self):
        for widget in self.frame.winfo_children():
            widget.destroy()