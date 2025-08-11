import tkinter
from tkinter import ttk
from tkinterweb import HtmlFrame
from PIL import ImageTk, Image
import fileHandler
import math

class newTab():
    def __init__(self,tab,stringVar,startpage):
        ## TODO: system to look through history and list top x most visited pages (x set by user, default 8)
        self.ShortcutButtons = []
        self.PopularPages = []
        self.columnFrames = []
        self.newestImages = []
        self.newestImageData = []
        self.ShowAmount = 8
        self.chosenURL = "about:blank"
        # Internal var
        newestObjectText = ""
        # Frame
        self.newTabFrame = tkinter.Frame(tab)

        # New tab design

        self.splashText = ttk.Label(self.newTabFrame,text="Flamingearth Browser",font=("TkDefaultFont",32))
        self.splashText.pack()
        self.vText = ttk.Label(self.newTabFrame,text="v1.00a")
        self.vText.pack()

        self.midBar = ttk.Frame(self.newTabFrame)
        self.midBar.pack()

        ##self.newTabAddressBar = ttk.Entry(self.midBar,textvariable = self.currentAddress)
        ##self.newTabAddressBar.bind("<Return>")
        ##self.newTabAddressBar.pack(fill = "x",side = "left")
        ##self.newTabGobutton = ttk.Button(self.midBar,style="Accent.TButton",text = "Go")
        ##self.newTabGobutton.pack(side="right")
        self.splashText = ttk.Label(self.newTabFrame,text="Most viewed pages",font=("TkDefaultFont",16))
        self.splashText.pack()
        self.PopularFrame = ttk.Frame(self.newTabFrame)
        self.PopularFrame.pack(fill="both")
        for r in range(math.ceil((self.ShowAmount)/4)):
            self.columnFrames.append(ttk.Frame(self.PopularFrame))
            self.columnFrames[r].pack(side = "top",expand =1)
            for c in range(4):
                i = c+(4*r)
                url = "about:blank"
                historyItem = 0
                title = "Unset"
                icon = tkinter.PhotoImage(file=fileHandler.noIcon)
                if i<len(fileHandler.historyRanked):
                    try:
                        url = fileHandler.historyRanked[i]
                        historyItem = fileHandler.historyURL.index(url)
                        title = fileHandler.historyTitles[historyItem]
                        icon = tkinter.PhotoImage(file=fileHandler.historyIcons[historyItem])
                        self.newestImages.append(icon)
                    except IndexError:
                        title = "Unset"
                        self.newestImageData.append(Image.open(fileHandler.noShortcut))
                        self.newestImages.append(ImageTk.PhotoImage(image=self.newestImageData[i]))
                else:
                    title = "Unset"
                    self.newestImageData.append(icon)
                    self.newestImages.append(icon)
                self.ShortcutButtons.append(ttk.Button(self.columnFrames[-1],text=title,image=icon,compound="top",command=lambda page = url:self.goToPage(page),width=8))
                self.ShortcutButtons[-1].pack(side = "left",padx = 5,pady = 5)

        self.quickAccess = ttk.Button()

    def goToPage(self,page):
        print(f"[NewTab] URL clicked {page}")
        self.chosenURL = page
        self.newTabFrame.event_generate("<<URLChanged>>")