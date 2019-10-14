import threading
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
from tkinter.font import Font
from tkinter.ttk import Scrollbar

from ttkthemes import themed_style

from src.controller import sorting_controller, root_controller
from src.tools.back_end import error_checker
import src.tools.display.display_tools as tools
from src.user_interface.data_display import DataDisplay
from src.user_interface import configurations as config

ENTRY_WIDTH = 12
SCREEN_DIMENSIONS = "1000x800"
SYSTEM_DELAY = 100

class Selector:

    def __init__(self, root):
        self.root = root
        self.win = ttk.Frame(self.root)
        self.win.pack(fill=tk.BOTH, expand=tk.TRUE)
        self.filename1 = ""
        self.filename2 = ""
        self.button1 = None
        self.button2 = None
        self.index = 0
        self.num_boxes = 0
        self.data_display = DataDisplay(win=self.win, root=self.root)
        self.initialize_maps()
        self.initialize_display()
        self.status_message = tk.StringVar()
        self.status_message.set(config.IDLE)

    def initialize_maps(self):

        self.KEYS_TO_ARGS = {
                            config.FILENAME_1_ARG_KEY: self.filename1,
                            config.FILENAME_2_ARG_KEY: self.filename2,
                            config.NUM_BOXES_ARG_KEY: self.num_boxes
                            }

        self.FUNCTION_MAP = {
            "Sort images by QR": sorting_controller.SortImgByQR(),
            "Sort images by folder": sorting_controller.SortImgToFolders(),
            "Sort folders by QR": sorting_controller.SortFoldersByQR(),
            "Merge QR sorted data": sorting_controller.MergeData(),
            "Generate Root Data": root_controller.GetRootData(self.data_display)
                            }

        self.CHOICES = list(self.FUNCTION_MAP.keys())

        self.ARGS_MAP = {
            "Sort images by QR": (config.FILENAME_1_ARG_KEY, config.FILENAME_2_ARG_KEY, config.NUM_BOXES_ARG_KEY),
            "Sort images by folder": (config.FILENAME_1_ARG_KEY, config.FILENAME_2_ARG_KEY, config.NUM_BOXES_ARG_KEY),
            "Sort folders by QR": (config.FILENAME_1_ARG_KEY, config.FILENAME_2_ARG_KEY),
            "Merge QR sorted data": (config.FILENAME_1_ARG_KEY, config.FILENAME_2_ARG_KEY),
            "Generate Root Data": (config.FILENAME_1_ARG_KEY, config.FILENAME_2_ARG_KEY)
        }

    def initialize_display(self):
        self.root.style.configure(config.BUTTON_STYLE, font=config.BUTTON_FONT)
        self.root.style.configure(config.LABEL_FRAME_STYLE, font=config.TITLE_FONT)

        title_frame = ttk.Frame(self.win)
        tools.pack_blank_row(title_frame)
        label = ttk.Label(title_frame, text = config.TITLE, font=config.TITLE_FONT, foreground=config.TEXT_COLOR)
        label.pack(side=tk.TOP, anchor=tk.CENTER)
        tools.pack_blank_row(title_frame)
        title_frame.pack(side=tk.TOP)

        command_chooser_frame = ttk.Frame(self.win)
        label = ttk.Label(command_chooser_frame, text=config.COMMAND_CHOOSER_LABEL, font=config.COMMAND_CHOOSER_FONT, foreground=config.TEXT_COLOR)
        label.pack(side=tk.TOP, anchor=tk.CENTER)
        tools.pack_blank_row(command_chooser_frame)
        self.command = tk.StringVar()
        self.command.set(self.CHOICES[config.DEFAULT_CHOICE_INDEX])
        popupMenu = ttk.Combobox(command_chooser_frame, text="Choose action", textvariable=self.command, values=self.CHOICES)
        popupMenu.bind('<<ComboboxSelected>>', lambda args = None: self.change_label_text(args))
        popupMenu.pack(side=tk.TOP, anchor=tk.CENTER)
        tools.pack_blank_row(command_chooser_frame, rows=2)
        command_chooser_frame.pack(side=tk.TOP)

        ttk.Separator(self.win, orient=tk.HORIZONTAL).pack(fill=tk.X)
        tools.pack_blank_row(self.win)

        selector_frame = ttk.Frame(self.win)
        self.button1_label = ttk.Label(selector_frame, text=config.BUTTON1_LABELS[config.DEFAULT_CHOICE_INDEX], font=config.MAIN_FONT, foreground=config.TEXT_COLOR)
        self.button1_label.grid(row=config.LABEL_ROW, column=config.BUTTON1_COL)
        self.button2_label = ttk.Label(selector_frame, text=config.BUTTON2_LABELS[config.DEFAULT_CHOICE_INDEX], font=config.MAIN_FONT, foreground=config.TEXT_COLOR)
        self.button2_label.grid(row=config.LABEL_ROW, column=config.BUTTON2_COL)
        tools.grid_empty_cell(selector_frame, 1, 0)
        entry_label = ttk.Label(selector_frame, text="Number of Boxes", font=config.MAIN_FONT, foreground=config.TEXT_COLOR)
        entry_label.grid(row = config.LABEL_ROW, column = config.ENTRY_COL)
        self.make_chooser_button1(selector_frame, text=config.NO_FILE_SELECTED)
        tools.grid_empty_cell(selector_frame, col=config.BUTTON1_COL + 1, row=0)
        self.make_chooser_button2(selector_frame, text=config.NO_FILE_SELECTED)
        tools.grid_empty_cell(selector_frame, col=config.BUTTON2_COL + 1, row=0)
        self.entry = tools.create_entry_box(selector_frame, row=config.WIDGET_ROW, column=config.ENTRY_COL)
        self.num_boxes = self.entry.get()
        self.KEYS_TO_ARGS[config.NUM_BOXES_ARG_KEY] = self.num_boxes
        selector_frame.pack(side=tk.TOP, anchor=tk.CENTER)

        tools.pack_blank_row(self.win, rows=2)
        self.data_display.frame.pack(side=tk.TOP, expand=tk.FALSE)
        tools.pack_blank_row(self.win)

        base_frame = ttk.Frame(self.win)
        self.status_message = tk.StringVar()
        self.status_message.set(config.IDLE)
        self.status_label = ttk.Label(base_frame, textvariable=self.status_message)
        self.status_label.pack(side=tk.TOP, anchor=tk.CENTER)
        self.make_run_button(base_frame)
        tools.pack_blank_row(base_frame)
        base_frame.pack(side=tk.TOP, anchor = tk.CENTER)


    def make_chooser_button1(self, win, text):
        self.button1 = ttk.Button(win, text=text, command=self.file_chooser1, style=config.BUTTON_STYLE)
        self.button1.grid(column=config.BUTTON1_COL, row=config.WIDGET_ROW)

    def make_chooser_button2(self, win, text):
        self.button2 = ttk.Button(win, text=text, command=self.file_chooser2, style=config.BUTTON_STYLE)
        self.button2.grid(column=config.BUTTON2_COL, row=config.WIDGET_ROW)

    def make_run_button(self, win):
        button = ttk.Button(win, text="RUN", command = lambda args=None: self.run(args), style=config.BUTTON_STYLE)
        button.pack(side=tk.TOP, anchor=tk.CENTER)

    def run(self, args):
        entry = self.entry.get()
        error_message = error_checker.validate_inputs(self.filename1, self.filename2, entry, index=self.index)

        if error_message is not "":
            tools.display_error_box(error_message)
            return
        try:
            self.num_boxes = int(entry)
        except:
            self.num_boxes = 0
        self.status_message.set(config.PROCESSING)
        self.status_label.configure(textvariable=self.status_message)
        self.root.after(SYSTEM_DELAY, self.start_command_thread)

    def start_command_thread(self):
        command_thread = threading.Thread(target=self.perform_commands, args=())
        command_thread.start()

    def perform_commands(self):
        self.status_message.set(config.PROCESSING)
        self.status_label.configure(textvariable=self.status_message)
        function = self.FUNCTION_MAP[self.command.get()]
        arg_keys = self.ARGS_MAP[self.command.get()]
        args = []
        for key in arg_keys:
            arg = self.KEYS_TO_ARGS[key]
            args.append(arg)
        error_message = function.call(args=args)
        if len(error_message) > 0:
            self.status_message.set(config.ABORTED)
            self.status_label.configure(textvariable=self.status_message)
            tools.display_error_box(error_message)
        self.status_message.set(config.COMPLETED)
        self.status_label.configure(textvariable=self.status_message)


    def file_chooser1(self):
        self.filename1 = filedialog.askdirectory()
        self.KEYS_TO_ARGS[config.FILENAME_1_ARG_KEY] = self.filename1
        if self.filename1 == "":
            text = config.NO_FILE_SELECTED
        else:
            text = self.filename1
        self.button1['text'] = text

    def file_chooser2(self):
        self.filename2 = filedialog.askdirectory()
        self.KEYS_TO_ARGS[config.FILENAME_2_ARG_KEY] = self.filename2
        if self.filename2 == "":
            text = config.NO_FILE_SELECTED
        else:
            text = self.filename2
        self.button2['text'] = self.filename2

    def change_label_text(self, args):
        command = self.command.get()
        for index in range(len(self.CHOICES)):
            if command == self.CHOICES[index]:
                break
        self.index = index
        self.command.set(self.CHOICES[index])
        self.button1_label['text'] = config.BUTTON1_LABELS[index]
        self.button2_label['text'] = config.BUTTON2_LABELS[index]
        if index < 2:
            self.entry['state'] = tk.NORMAL
        else:
            self.entry['state'] = tk.DISABLED