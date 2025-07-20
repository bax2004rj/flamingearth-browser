import tkinter
from tkinter import ttk
import fileHandler

class History:
    def __init__(self,tab):
        self.history_frame = ttk.Frame(tab)

        self.topbar = ttk.Frame(self.history_frame)
        self.topbar.pack(side="top", fill="x")

        self.sidebar = tkinter.Frame(self.history_frame)
        self.sidebar.pack(side="left", fill="y")

        self.top_label = ttk.Label(self.topbar, text="History",font=("TkDefaultFont", 16))
        self.top_label.pack(side="left", padx=10)

        self.search_bar = ttk.Entry(self.topbar)
        self.search_bar.pack()
        self.search_bar.insert(0, "Search through history…")

        self.datesList = tkinter.Listbox(self.sidebar)
        self.datesList.pack(fill="both", expand=True)
        self.datesList.insert(0, "Today")
        self.datesList.insert(1, "Yesterday")
        self.datesList.insert(2, "Last 7 days")
        self.datesList.insert(3, "Last 30 days")
        self.datesList.insert(4, "All time")

        self.clear_button = ttk.Button(self.sidebar, text="Clear History", command=self.clear_history)
        self.clear_button.pack(side="bottom", fill="x")

        self.history_list = tkinter.Canvas(self.history_frame)
        self.history_list.pack(side="right", fill="both", expand=True)

        self.history_scrollbar = ttk.Scrollbar(self.history_list, orient="vertical", command=self.history_list.yview)
        self.history_scrollbar.pack(side="right", fill="y")

    def clear_history(self):
        continue_confirm = tkinter.messagebox.askyesno("Clear History", "Are you sure you want to clear your history?")
        if continue_confirm:
            fileHandler.clearHistory()

        