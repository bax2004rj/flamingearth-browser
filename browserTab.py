import tkinter
from tkinter import ttk
from tkinterweb import HtmlFrame

crashHandling = True
homePage = "https://www.google.com"

class newTab():
    def __init__(self,tab,stringVar,startpage):
        self.addressObject = tkinter.Frame(tab)
        self.addressObject.pack(side = "top",fill = "x")
        
        self.currentAddress = tkinter.StringVar(tab,value = startpage)

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

        self.zoomButton = ttk.Menubutton(self.addressBar,text = "🔍",menu = self.zoomMenu)

        self.homeButton = ttk.Button(self.addressBar,text = "⌂️",command = self.goHome)
        self.homeButton.pack(side = "right")

        self.refreshButton = ttk.Button(self.addressBar,text = "↺",command= self.refresh)
        self.refreshButton.pack(side="right")

        self.gobutton = ttk.Button(self.addressBar,style="Accent.TButton",text = "Go",command=newTab.goToPage)
        self.gobutton.pack(side="right")

        # Setup browser object
        
        self.browser = HtmlFrame(tab)
        self.browser.pack(fill="both", expand=True)
        self.browser.on_url_change(self.changeUrl)

        self.cMenu = tkinter.Menu(self.browser)
        self.cMenu.add_command(label="Copy")
        self.cMenu.add_separator()
        self.cMenu.add_command(label="Back")
        self.cMenu.add_command(label="Forward")
        self.cMenu.add_command(label="Reload",command=self.refresh)
        self.cMenu.add_separator()
        self.cMenu.add_command(label="Find")
        self.cMenu.add_cascade(label="Zoom",menu=self.zoomMenu)


        self.browser.enable_crash_prevention(isenabled=crashHandling)
        self.browser.load_website(startpage)

        self.browser.bind("<Button-3>",self.contextMenu)
    
    def contextMenu(self,event):
        try:
            self.cMenu.tk_popup(event.x_root,event.y_root,0)
        finally:
             self.cMenu.grab_release()

    def goToPage(self,event = None):
        self.page = self.currentAddress.get()
        self.browser.load_website(self.page)
    
    def refresh(self):
        self.browser.load_website(self.page)
    
    def goHome(self):
        self.browser.load_website(homePage)

    def zoomIn(self):
        self.zoom += .25
        self.percentZoom = self.zoom*100
        self.zoomMenu.entryconfig(0,label = "Zoom level: %d%%"%(self.percentZoom))
        self.browser.set_zoom(self.zoom)
        self.zoomButton.pack(side = "right")
    
    def zoomOut(self):
        self.zoom -= .25
        self.percentZoom = self.zoom*100
        self.zoomMenu.entryconfig(0,label = "Zoom level: %d%%"%(self.percentZoom))
        self.browser.set_zoom(self.zoom)
        self.zoomButton.pack(side = "right")
    
    def zoomReset(self):
        self.zoom = 1
        self.percentZoom = self.zoom*100
        self.zoomMenu.entryconfig(0,label = "Zoom level: %d%%"%(self.percentZoom))
        self.browser.set_zoom(self.zoom)
        self.zoomButton.pack_forget()

    def changeUrl(self,title):
        self.currentAddress.set(title)
