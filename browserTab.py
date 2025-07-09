import tkinter
from tkinter import ttk
from tkinterweb import HtmlFrame

crashHandling = True

class newTab():
    def __init__(self,tab,zoomMenu,backCmd,fwdCmd):

        # Setup browser object
        
        self.browser = HtmlFrame(tab,javascript_enabled = True)
        #self.browser.pack(fill="both", expand=True)

        self.zoom = 1
        self.loading = False
        self.browser.bind("<<DownloadingResource>>", self.isLoading)
        self.browser.bind("<<DoneLoading>>", self.noLongerLoading)

        # Right click context menu
        self.cMenu = tkinter.Menu(self.browser)
        self.cMenu.add_command(label="Copy")
        self.cMenu.add_separator()
        self.cMenu.add_command(label="Back",command=backCmd)
        self.cMenu.add_command(label="Forward",command=fwdCmd)
        self.cMenu.add_command(label="Reload",command=self.refresh)
        self.cMenu.add_separator()
        self.cMenu.add_command(label="Find", command=self.toggleFindBar)
        self.cMenu.add_cascade(label="Zoom",menu=zoomMenu)

        self.browser.bind("<Button-3>",self.contextMenu)
    
        # Find toolbar
        self.findSelection = 1
        self.foundItems = 0
        self.ignoreCaseVar = tkinter.BooleanVar(tab,True)
        self.highlightVar = tkinter.BooleanVar(tab,False)
        self.findMenuVisible = False

        self.findMenu = tkinter.Frame(tab)
        self.findLabel = ttk.Label(self.findMenu,text="Find:")
        self.findLabel.pack(side="left")
        self.findTextVar = tkinter.StringVar(tab,"")
        self.findTextVar.trace_add("write",self.find)  # Trace changes to
        self.findSearchBar = ttk.Entry(self.findMenu, textvariable=self.findTextVar)
        self.findSearchBar.pack(side="left")
        self.ignoreCaseSwitch = ttk.Checkbutton(self.findMenu,text="Ignore case",onvalue=True,offvalue=False,variable=self.ignoreCaseVar, command=self.find)
        self.ignoreCaseSwitch.pack(side="left")
        self.highlightSwitch = ttk.Checkbutton(self.findMenu,text="Highlight all items",onvalue=True,offvalue=False,variable=self.highlightVar, command=self.find)
        self.highlightSwitch.pack(side="left")
        self.nextButton = ttk.Button(self.findMenu,text="↓",command= self.findNext)
        self.nextButton.pack(side="left")
        self.previousButton = ttk.Button(self.findMenu,text="↑",command=self.findPrevious)
        self.previousButton.pack(side="left")
        self.itemsFoundLabel = ttk.Label(self.findMenu,text="No items found")
        self.itemsFoundLabel.pack(side="left")
        self.findSearchBar.bind("<Return>",self.find())
        self.findSearchBar.bind("<KeyRelease>",self.find()) # Start searching while typing
        self.closeFindButton = ttk.Button(self.findMenu,text="x",command=self.toggleFindBar)
        self.closeFindButton.pack(side="right")
    def showBrowserView(self):
        self.browser.pack(fill="both", expand=True)
    
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
            self.loading = False # Create event to notify browser that loading has stopped
            self.browser.event_generate("<<DoneLoading>>")
        else:
            self.browser.load_website(self.browser.current_url)
    
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

    def toggleFindBar(self):
        if not self.findMenuVisible:
             self.findMenu.pack(side="bottom", fill="x")
             self.findMenuVisible = True
        else:
             self.findMenu.pack_forget()
             self.findMenuVisible = False
            
    def find(self,var = None, index = None, mode = None):
        searchTerm = self.findTextVar.get()
        ignoreCase = self.ignoreCaseVar.get()
        highlightAll = self.highlightVar.get()
        self.foundItems =self.browser.find_text(searchTerm,select= self.findSelection, ignore_case=ignoreCase, highlight_all=highlightAll)
        if self.foundItems == 0:
            self.itemsFoundLabel.configure(text="No items found")
            self.findSelection = 1
        elif self.findSelection > self.foundItems:
            self.findSelection = self.foundItems
        else:
            self.itemsFoundLabel.configure(text=f"{self.findSelection} of {self.foundItems} found")

    def findNext(self):
        if self.findSelection < self.foundItems:
            self.findSelection += 1
        else:
            self.findSelection = 1
        self.find()
    
    def findPrevious(self):
        if self.findSelection <= 1:
            self.findSelection = self.foundItems
        else:
            self.findSelection -= 1
        self.find()