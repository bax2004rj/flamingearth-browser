import tkinter
from tkinter import ttk
from tkinterweb import HtmlFrame

crashHandling = True
homePage = "https://www.google.com"

class newTab():
    def __init__(self,tab,stringVar,startpage,zoomMenu):

        # Setup browser object
        
        self.browser = HtmlFrame(tab)
        #self.browser.pack(fill="both", expand=True)
        self.zoom = 1
        self.percentZoom = self.zoom*100

        self.cMenu = tkinter.Menu(self.browser)
        self.cMenu.add_command(label="Copy")
        self.cMenu.add_separator()
        self.cMenu.add_command(label="Back")
        self.cMenu.add_command(label="Forward")
        self.cMenu.add_command(label="Reload",command=self.refresh)
        self.cMenu.add_separator()
        self.cMenu.add_command(label="Find")
        self.cMenu.add_cascade(label="Zoom",menu=zoomMenu)

        self.browser.bind("<Button-3>",self.contextMenu)
        self.browser.bind("<<UrlChanged>>",self.changeUrl)
    
    def showBrowserView(self):
        self.browser.pack(fill="both", expand=True)
        self.browser.on_url_change(self.changeUrl)
        self.browser.enable_crash_prevention(isenabled=crashHandling)
    
    def hideBrowserView(self):
        self.browser.pack_forget()

    def contextMenu(self,event):
        try:
            self.cMenu.tk_popup(event.x_root,event.y_root,0)
        finally:
             self.cMenu.grab_release()

    def goToPage(self,page,event = None):
        self.page = page
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
        self.browser.load_website(title)
    
    #Send link clicked event to parent tabFrame
    def linkClicked(self,event):
        print("[BROWSERVIEW.PY] Link clicked:", event.url)
        self.event_generate("<<LinkClicked>>", when="tail", url=event.url)
