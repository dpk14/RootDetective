from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

ENTRY_WIDTH = 12

def pack_blank_row(frame, rows=1):
    for row in range(rows):
        label = ttk.Label(frame, text="")
        label.pack(side=tk.TOP, anchor=tk.CENTER)

def pack_blank_col(frame, cols=1):
    for row in range(cols):
        blank_frame = ttk.Frame(frame)
        blank_frame.pack(side=tk.LEFT)
        label = ttk.Label(blank_frame, text="       ")
        label.pack(side=tk.LEFT, anchor=tk.CENTER)

def grid_empty_cell(frame, row, col):
    label = ttk.Label(frame, text="           ")
    label.grid(column=col, row = row)

def display_error_box(error_message):
    messagebox.showerror("Error", error_message)

def create_label(win, text):
    label = ttk.Label(win, text=text)
    label.pack(side=tk.LEFT)

def create_entry_box(win, row, column):
    variable = tk.StringVar()
    entry = ttk.Entry(win, width=ENTRY_WIDTH, textvariable=variable)
    entry.grid(row=row, column=column)
    return entry
