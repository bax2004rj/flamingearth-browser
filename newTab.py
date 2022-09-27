import tkinter
from tkinter import ttk
from tkinterweb import HtmlFrame

class newTab():
    def __init__(self,tab,stringVar,startpage):
        self.addressObject = tkinter.Frame(tab)
        self.addressObject.pack(side = "top",fill = "x")
        
        self.currentAddress = tkinter.StringVar(tab,value = startpage)

        self.addressBar = ttk.Combobox(self.addressObject,textvariable = self.currentAddress)
        self.addressBar.bind("<Return>")
        self.addressBar.pack(fill = "x")

        self.historyMenu = tkinter.Menu(self.addressBar)
        self.historyMenu.add_command(label="Clear history")

        self.downloadMenu = tkinter.Menu(self.addressBar)
        self.downloadMenu.add_command(label="Clear downloads")

        self.zoom = 1

        self.zoomMenu = tkinter.Menu(self.addressBar)
        self.zoomMenu.add_command(label="Zoom level: 100%",state="disabled")
        self.zoomMenu.add_command(label="+25%")
        self.zoomMenu.add_command(label="Reset")
        self.zoomMenu.add_command(label="-25%")

        self.bookmarksMenu = tkinter.Menu(self.addressBar)

        self.hamburgerMenu = tkinter.Menu(self.addressBar)
        self.hamburgerMenu.add_command(label="New tab")
        self.hamburgerMenu.add_command(label="New window")
        self.hamburgerMenu.add_separator()
        self.hamburgerMenu.add_cascade(label="History",menu=self.historyMenu)
        self.hamburgerMenu.add_cascade(label="Downloads",menu=self.downloadMenu)
        self.hamburgerMenu.add_cascade(label="Bookmarks",menu=self.bookmarksMenu)
        self.hamburgerMenu.add_separator()
        self.hamburgerMenu.add_command(label="Find")
        self.hamburgerMenu.add_cascade(label="Zoom",menu=self.zoomMenu,state="disabled")

        self.menuButton = ttk.Menubutton(self.addressBar,text = "≡",menu = self.hamburgerMenu)
        self.menuButton.pack(side = "right")

        self.downloadButton = ttk.Menubutton(self.addressBar,text = "↓",menu = self.downloadMenu)
        self.downloadButton.pack(side = "right")

        self.zoomButton = ttk.Menubutton(self.addressBar,text = "🔍",menu = self.zoomMenu)

        self.homeButton = ttk.Button(self.addressBar,text = "⌂️")
        self.homeButton.pack(side = "right")

        self.gobutton = ttk.Button(self.addressBar,style="Accent.TButton",text = "Go")
        self.gobutton.pack(side="right")

        # New tab design

        self.splashText = ttk.Label(tab,text="Welcome to the Flamingearth browser",font=("TkDefaultFont",32))
        self.splashText.pack()
        self.vText = ttk.Label(tab,text="v1.00a")
        self.vText.pack()

        self.midBar = ttk.Frame(tab)
        self.midBar.pack()

        self.newTabAddressBar = ttk.Combobox(self.midBar,textvariable = self.currentAddress)
        self.newTabAddressBar.bind("<Return>")
        self.newTabAddressBar.pack()

