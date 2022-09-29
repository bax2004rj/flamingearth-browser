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
        # Internal var
        newestObjectText = ""

        ## UI elements 
        self.addressObject = tkinter.Frame(tab)
        self.addressObject.pack(side = "top",fill = "x")
        
        self.currentAddress = tkinter.StringVar(tab,value = startpage)

        self.historyMenu = tkinter.Menu(self.addressObject)
        self.historyMenu.add_command(label="Clear history")

        self.downloadMenu = tkinter.Menu(self.addressObject)
        self.downloadMenu.add_command(label="Clear downloads")

        self.zoom = 1

        self.zoomMenu = tkinter.Menu(self.addressObject)
        self.zoomMenu.add_command(label="Zoom level: 100%",state="disabled")
        self.zoomMenu.add_command(label="+25%")
        self.zoomMenu.add_command(label="Reset")
        self.zoomMenu.add_command(label="-25%")

        self.bookmarksMenu = tkinter.Menu(self.addressObject)

        self.hamburgerMenu = tkinter.Menu(self.addressObject)
        self.hamburgerMenu.add_command(label="New tab")
        self.hamburgerMenu.add_command(label="New window")
        self.hamburgerMenu.add_separator()
        self.hamburgerMenu.add_cascade(label="History",menu=self.historyMenu)
        self.hamburgerMenu.add_cascade(label="Downloads",menu=self.downloadMenu)
        self.hamburgerMenu.add_cascade(label="Bookmarks",menu=self.bookmarksMenu)
        self.hamburgerMenu.add_separator()
        self.hamburgerMenu.add_command(label="Find")
        self.hamburgerMenu.add_cascade(label="Zoom",menu=self.zoomMenu,state="disabled")

        self.menuButton = ttk.Menubutton(self.addressObject,text = "≡",menu = self.hamburgerMenu)
        self.menuButton.pack(side = "right")

        self.downloadButton = ttk.Menubutton(self.addressObject,text = "↓",menu = self.downloadMenu)
        self.downloadButton.pack(side = "right")

        self.zoomButton = ttk.Menubutton(self.addressObject,text = "🔍",menu = self.zoomMenu)

        self.homeButton = ttk.Button(self.addressObject,text = "⌂️")
        self.homeButton.pack(side = "right")

        # New tab design

        self.splashText = ttk.Label(tab,text="Welcome to the Flamingearth browser",font=("TkDefaultFont",32))
        self.splashText.pack()
        self.vText = ttk.Label(tab,text="v1.00a")
        self.vText.pack()

        self.midBar = ttk.Frame(tab)
        self.midBar.pack()

        self.newTabAddressBar = ttk.Entry(self.midBar,textvariable = self.currentAddress)
        self.newTabAddressBar.bind("<Return>")
        self.newTabAddressBar.pack(fill = "x",side = "left")
        self.newTabGobutton = ttk.Button(self.midBar,style="Accent.TButton",text = "Go")
        self.newTabGobutton.pack(side="right")
        self.splashText = ttk.Label(tab,text="Most viewed pages",font=("TkDefaultFont",16))
        self.splashText.pack()
        self.PopularFrame = ttk.Frame(tab)
        self.PopularFrame.pack(fill="both")
        for r in range(math.ceil((self.ShowAmount)/4)):
            self.columnFrames.append(ttk.Frame(self.PopularFrame))
            self.columnFrames[r].pack(side = "top",expand =1)
            for c in range(4):
                i = c+(4*r)
                if i<len(self.PopularPages):
                    newestObjectText = self.PopularPages[i]
                    self.newestImageData.append(Image.open(fileHandler.noIcon))
                    self.newestImages.append(ImageTk.PhotoImage(image=self.newestImageData[i]))
                    print("Preset success")
                else:
                    newestObjectText = "Unset"
                    self.newestImageData.append(Image.open(fileHandler.noShortcut))
                    self.newestImages.append(ImageTk.PhotoImage(image=self.newestImageData[i]))
                self.ShortcutButtons.append(ttk.Button(self.columnFrames[-1],text=newestObjectText,image=self.newestImages[i],compound="top"))
                self.ShortcutButtons[-1].pack(side = "left")

        self.quickAccess = ttk.Button()

