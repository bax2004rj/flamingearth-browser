import tkinter
from tkinter import ttk
import newTab
import browserTab
import settings
import fileHandler

class newFrame:
    def __init__(self,tabFrame,frameVar,startpage):
        self.homepage = startpage
        self.sessionTitles = []
        self.sessionUrls = []

        self.addressObject = tkinter.Frame(tabFrame)
        self.addressObject.pack(side = "top",fill = "x")
        
        self.currentAddress = tkinter.StringVar(tabFrame,value = startpage)

        self.addressBar = ttk.Combobox(self.addressObject,textvariable = self.currentAddress,values = self.sessionUrls)
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
        self.hamburgerMenu.add_command(label="Settings",command=lambda: self.goToPage("flamingearth://settings"))

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
        self.browserView = browserTab.newTab(tabFrame,None,startpage,self.zoomMenu)
        self.settingsFrame = settings.Settings(tabFrame)

        tabFrame.bind("<<LinkClicked>>",self.pageChanged) # Bind link clicked event to pageChanged method
    
    def goToPage(self,event=None): #Handle going to pages
        page = self.addressBar.get()
        print(page)
        if page != "flamingearth://newtab":
            try:
                self.newtab.newTabFrame.pack_forget()
            except Exception:
                print("newtab frame did not need to be destroyed")
        if page[:4] == "http" or page[:4] == "file":
            try:
                self.browserView.showBrowserView()
                self.zoomButton.configure(state="normal") # Enable zoom menu
            except Exception:
                pass   
            self.browserView.changeUrl(page)
            self.zoomButton.configure(state="disabled") # Disable zoom menu
        elif page[:12] == "flamingearth":
            subpage = page.lstrip("flamingearth://")
            self.browserView.hideBrowserView()
            if subpage == "newtab":
                self.newtab.newTabFrame.pack(fill="both", expand=True)
                self.browserView.hideBrowserView()
            elif subpage == "settings":
                self.newtab.newTabFrame.pack_forget()
                self.browserView.hideBrowserView()
                self.settingsFrame.pack(fill="both", expand=True)
    
    def pageChanged(self,event):
        self.currentAddress.set(event.url)
        self.seesionurls.append(event.url)

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