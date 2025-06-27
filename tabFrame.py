import tkinter
from tkinter import ttk
import newTab
import browserTab

class newFrame:
    def __init__(self,tabFrame,frameVar,startpage):
        self.homepage = startpage
            
        self.addressObject = tkinter.Frame(tabFrame)
        self.addressObject.pack(side = "top",fill = "x")
        
        self.currentAddress = tkinter.StringVar(tabFrame,value = startpage)

        self.addressBar = ttk.Combobox(self.addressObject,textvariable = self.currentAddress)
        self.addressBar.bind("<Return>",self.goToPage)
        self.addressBar.pack(fill = "x")

        self.historyMenu = tkinter.Menu(self.addressBar)
        self.historyMenu.add_command(label="Clear history")

        self.downloadMenu = tkinter.Menu(self.addressBar)
        self.downloadMenu.add_command(label="Clear downloads")

        self.zoom = 1

        self.zoomMenu = tkinter.Menu(self.addressBar)
        self.zoomMenu.add_command(label="Zoom level: 100%",state="disabled")
        self.zoomMenu.add_command(label="+25%",command = self.zoomIn)
        self.zoomMenu.add_command(label="Reset",command = self.zoomReset)
        self.zoomMenu.add_command(label="-25%",command = self.zoomOut)

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
        self.hamburgerMenu.add_cascade(label="Zoom",menu=self.zoomMenu)

        self.menuButton = ttk.Menubutton(self.addressBar,text = "≡",menu = self.hamburgerMenu)
        self.menuButton.pack(side = "right")

        self.downloadButton = ttk.Menubutton(self.addressBar,text = "↓",menu = self.downloadMenu)
        self.downloadButton.pack(side = "right")

        self.zoomButton = ttk.Menubutton(self.addressBar,text = "🔍",menu = self.zoomMenu, state="disabled")

        self.homeButton = ttk.Button(self.addressBar,text = "⌂️",command = self.goHome)
        self.homeButton.pack(side = "right")

        self.refreshButton = ttk.Button(self.addressBar,text = "↺",command= self.refresh)
        self.refreshButton.pack(side="right")

        self.gobutton = ttk.Button(self.addressBar,style="Accent.TButton",text = "Go",command=self.goToPage)
        self.gobutton.pack(side="right")

        self.newtab = newTab.newTab(tabFrame,frameVar,startpage)
    
    def goToPage(self,page = "flamingearth://newtab"):
        print("Go to page")
    
    def goHome(self):
        self.goToPage(self.homepage)
    
    def refresh(self):
        self.goToPage(self.homepage)
    
    def zoomIn(self):
        print("zoom in")
    
    def zoomReset(self):
        print("zoom reset")

    def zoomOut(self):
        print("zoom out")