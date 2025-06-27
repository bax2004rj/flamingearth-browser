import tkinter
from tkinter import ttk
from tkinterweb import HtmlFrame

crashHandling = True
homePage = "https://www.google.com"

class newTab():
    def __init__(self,tab,stringVar,startpage):

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
