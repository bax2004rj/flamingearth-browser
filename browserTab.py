import tkinter
from tkinter import ttk
from tkinterweb import HtmlFrame

crashHandling = True
homePage = "https://www.google.com"

class newTab():
    def __init__(self,tab,zoomMenu):

        # Setup browser object
        
        self.browser = HtmlFrame(tab,javascript_enabled = True)
        #self.browser.pack(fill="both", expand=True)

        self.zoom = 1
        self.loading = False
        self.browser.bind("<<DownloadingResource>>", self.isLoading)
        self.browser.bind("<<DoneLoading>>", self.noLongerLoading)

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

    
    def refresh(self,event=None):
        if self.loading:
            self.browser.stop()
            self.loading = False # Create event to notify tabFrame that loading has stopped
            self.browser.event_generate("<<DoneLoading>>")
        else:
            self.browser.load_website(self.browser.current_url)
    
    def goHome(self):
        self.browser.load_website(homePage)

    def zoomIn(self,zoomMenu,zoomButton):
        self.zoom += .25
        self.percentZoom = self.zoom*100
        zoomMenu.entryconfig(1,label = "Zoom level: %d%%"%(self.percentZoom))
        self.browser.configure(zoom=self.zoom)
        zoomButton.pack(side = "right")
    
    def zoomOut(self,zoomMenu,zoomButton):
        self.zoom -= .25
        self.percentZoom = self.zoom*100
        zoomMenu.entryconfig(1,label = "Zoom level: %d%%"%(self.percentZoom))
        self.browser.configure(zoom=self.zoom)
        zoomButton.pack(side = "right")
    
    def zoomReset(self,zoomMenu,zoomButton):
        self.zoom = 1
        self.percentZoom = self.zoom*100
        zoomMenu.entryconfig(1,label = "Zoom level: %d%%"%(self.percentZoom))
        self.browser.configure(zoom=self.zoom)
        zoomButton.pack_forget()

    def changeUrl(self,title):
        self.browser.load_website(title)

    def isLoading(self,event):
        self.loading = True
    
    def noLongerLoading(self,event):
        self.loading = False