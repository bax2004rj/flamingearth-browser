import tkinter
from tkinter import ttk
import fileHandler
import sv_ttk
import os
import datetime

class History:
    def __init__(self,tab):
        self.history_frame = ttk.Frame(tab)

        self.topbar = ttk.Frame(self.history_frame, style = "Card.TFrame")
        self.topbar.pack(side="top", fill="x")

        self.sidebar = tkinter.Frame(self.history_frame)
        self.sidebar.pack(side="left", fill="y")

        self.progress = ttk.Progressbar(self.topbar)

        self.top_label = ttk.Label(self.topbar, text="History",font=("TkDefaultFont", 16))
        self.top_label.pack(side="left", padx=10)

        self.searchFrame = ttk.Frame(self.topbar)
        self.searchFrame.pack()

        self.search_bar = ttk.Entry(self.searchFrame)
        self.search_bar.pack(side = "left")
        self.search_bar.insert(0, "Search through history…")
        self.advancedButton = ttk.Button(self.searchFrame,text="Search options")
        self.advancedButton.pack(side="right")

        self.datesList = tkinter.Listbox(self.sidebar)
        self.datesList.pack(fill="both", expand=True)
        self.datesList.insert(0, "Today")
        self.datesList.insert(1, "Yesterday")
        self.datesList.insert(2, "Last 7 days")
        self.datesList.insert(3, "Last 30 days")
        self.datesList.insert(4, "All time")

        self.clear_button = ttk.Button(self.sidebar, text="Clear History", command=self.clear_history)
        self.clear_button.pack(side="bottom", fill="x")

        self.history_container = tkinter.Canvas(self.history_frame)
        self.history_container.pack(side="right", fill="both", expand=True)
        self.history_list = ttk.Frame(self.history_container)
        self.history_container.create_window((0,0), window=self.history_list, anchor="nw")
        self.history_seperators = []
        self.history_items = []

        self.history_scrollbar = ttk.Scrollbar(self.history_container, orient="vertical", command=self.history_container.yview)
        self.history_scrollbar.pack(side="right", fill="y")

    def clear_history(self):
        self.clearDialog = tkinter.Toplevel()
        self.clearDialog.title("Clear History")
        self.clearDialog.geometry("300x100")
        self.clearDialog.resizable(False, False)

        self.clearText = tkinter.Label(self.clearDialog, text="Delete all history from:")
        self.clearText.pack(side="top")

        self.times = ["Last hour", "Last 24 hours", "Last 7 days", "Last 4 weeks", "All time", "Custom"]
        self.timeDropdown = ttk.Combobox(self.clearDialog, values=self.times)
        self.timeDropdown.current(4)
        self.timeDropdown.pack(side="top")

        self.buttonFrame = ttk.Frame(self.clearDialog,style="Card.TFrame")
        self.buttonFrame.pack(side="bottom", fill="x")

        self.clearButton = ttk.Button(self.buttonFrame, text="Clear", style="Accent.TButton", command=fileHandler.clearHistory)
        self.clearButton.pack(side="right")
        self.cancelButton = ttk.Button(self.buttonFrame, text="Cancel", command=self.clearDialog.destroy)
        self.cancelButton.pack(side="right")


    def setDarkmode(self):
        if fileHandler.darkmode == True and fileHandler.tkinterTheme == "sv_ttk":
            sv_ttk.set_theme("dark") # Enable darkmode
        elif fileHandler.darkmode == False and fileHandler.tkinterTheme == "sv_ttk":
            sv_ttk.set_theme("light") # Enable lightmode
    
    def load_history(self):
        if len(fileHandler.historyURL) == 0:
            print("[History] No history")
            self.no_history_image = tkinter.PhotoImage(file=fileHandler.noShortcut)
            self.nohistorytext = tkinter.Label(self.history_list, text="No history found", font=("TkDefaultFont", 16), image=self.no_history_image, compound="top")
            self.nohistorytext.pack()
        else:
            self.progress.pack(side="top", fill="x")
            progress_steps = 100 / len(fileHandler.historyURL)
            self.history_seperators.clear()
            self.history_items.clear()

            self.history_seperators.append(tkinter.Label(self.history_list, text="Today", font=("TkDefaultFont", 14)))
            self.history_seperators[-1].pack(side = "top")
            previous_date = None
            for item in reversed(fileHandler.historyTimeAccessed):
                print(f"[History] Processing item {item}")
                itemNumber = fileHandler.historyTimeAccessed.index(item)
                itemDate = datetime.datetime.strptime(item,"%Y-%m-%d %H:%M:%S")
                self.progress.step(progress_steps)

                # Generate item frame
                self.history_items.append(ttk.Frame(self.history_list, style="Card.TFrame",cursor="hand2"))
                self.history_items[-1].iconImage = tkinter.PhotoImage(file=fileHandler.historyIcons[itemNumber] if os.path.exists(fileHandler.historyIcons[itemNumber]) else fileHandler.noIcon)
                self.history_items[-1].iconLabel = ttk.Label(self.history_items[-1], text=fileHandler.historyTitles[itemNumber],image=self.history_items[-1].iconImage, compound="left")
                self.history_items[-1].iconLabel.pack(side="top", fill = "x")
                self.history_items[-1].bottomFrame = ttk.Frame(self.history_items[-1])
                self.history_items[-1].bottomFrame.pack(side="top",fill="x")
                self.history_items[-1].timeLabel = tkinter.Label(self.history_items[-1].bottomFrame,text=f"{itemDate.time()}", font=("TkDefaultFont",10))
                self.history_items[-1].timeLabel.pack(side = "left")
                self.history_items[-1].seperator = ttk.Separator(self.history_items[-1].bottomFrame, orient="vertical")
                self.history_items[-1].seperator.pack(side="left")
                self.history_items[-1].urlLabel = tkinter.Label(self.history_items[-1].bottomFrame,text=f"{fileHandler.historyURL[itemNumber]}", font=("TkDefaultFont",10,"italic"))
                self.history_items[-1].urlLabel.pack(side = "left")

                #Detect changes in date and generate seperators
                if previous_date != itemDate.date() and previous_date is not None:
                    self.history_seperators.append(tkinter.Label(self.history_list, text=str(itemDate.date()), font=("TkDefaultFont", 14)))
                    self.history_seperators[-1].pack(side = "top")
                    print(f"[History] New date detected, adding seperator for {datetime.datetime.strftime(item,"%d %B %Y")}")
                    
                self.history_items[-1].pack(side = "top", anchor="w", fill="x")
                previous_date=itemDate.date()
            self.progress.pack_forget()
        