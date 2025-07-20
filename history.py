import tkinter
from tkinter import ttk
import fileHandler

class History:
    def __init__(self,tab):
        self.history_frame = ttk.Frame(tab)
        self.sidebar = tkinter.Frame(self.history_frame)
        self.sidebar.pack(side="left", fill="y")
        self.clear_button = ttk.Button(self.sidebar, text="Clear History", command=self.clear_history)
        self.clear_button.pack(side="bottom")

    def clear_history(self):
        continue_confirm = tkinter.messagebox.askyesno("Clear History", "Are you sure you want to clear your history?")
        if continue_confirm:
            fileHandler.clearHistory()

        