import tkinter
from tkinter import ttk
import datetime
import newTab
import browserTab
import settings
import fileHandler

class newFrame:
    def __init__(self,tabFrame,frameVar,startpage,tabid=0):
        self.homepage = startpage
        self.sessionTitles = []
        self.sessionUrls = []
        self.sessionBacks = -2
        self.doNotClearForwardHistory = False
        self.tab_id = tabid
        self.tabFrame = tabFrame
        self.tabTitle = "New Tab"

        self.addressObject = tkinter.Frame(tabFrame)
        self.addressObject.pack(side = "top",fill = "x")

        
        self.currentAddress = tkinter.StringVar(tabFrame,value = startpage)

        self.backbutton = ttk.Button(self.addressObject,text = "←",command = lambda: self.back())
        self.backbutton.pack(side = "left")
        self.forwardbutton = ttk.Button(self.addressObject,text = "→",command = lambda: self.forward())
        self.forwardbutton.pack(side = "left")
        self.backbutton.configure(state="disabled") # Disable back button
        self.forwardbutton.configure(state="disabled")

        self.addressBar = ttk.Combobox(self.addressObject,textvariable = self.currentAddress,values = self.sessionUrls)
        self.addressBar.bind("<Return>",self.goToPage)
        self.addressBar.pack(fill = "x")

        self.historyMenu = tkinter.Menu(self.addressBar)
        self.historyMenu.add_command(label="Clear history")

        self.downloadMenu = tkinter.Menu(self.addressBar)
        self.downloadMenu.add_command(label="Clear downloads")

        self.zoomMenu = tkinter.Menu(self.addressBar)

        self.bookmarksMenu = tkinter.Menu(self.addressBar)

        self.hamburgerMenu = tkinter.Menu(self.addressBar)

        self.newtab = newTab.newTab(tabFrame,frameVar,startpage)
        self.browserView = browserTab.newTab(tabFrame,self.zoomMenu)
        self.settingsFrame = settings.Settings(tabFrame)

        self.menuButton = ttk.Menubutton(self.addressBar,text = "≡",menu = self.hamburgerMenu)
        self.menuButton.pack(side = "right")

        self.downloadButton = ttk.Menubutton(self.addressBar,text = "↓",menu = self.downloadMenu)
        self.downloadButton.pack(side = "right")

        self.zoomButton = ttk.Menubutton(self.addressBar,text = "🔍",menu = self.zoomMenu, state="disabled")

        self.homeButton = ttk.Button(self.addressBar,text = "⌂️",command = self.goHome)
        self.homeButton.pack(side = "right")

        self.refreshButton = ttk.Button(self.addressBar,text = "↺",command= self.browserView.refresh)
        self.refreshButton.pack(side="right")

        ##self.gobutton = ttk.Button(self.addressBar,style="Accent.TButton",text = "Go",command=self.goToPage)
        ##self.gobutton.pack(side="right")

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

        self.zoomMenu.add_command(label="Zoom level: 100%",state="disabled") # When creating the menu entry, do NOT set state="disabled"
        self.zoomMenu.add_separator()
        self.zoomMenu.add_command(label="+25%",command = lambda: self.browserView.zoomIn(self.zoomMenu,self.zoomButton))
        self.zoomMenu.add_command(label="Reset",command = lambda: self.browserView.zoomReset(self.zoomMenu,self.zoomButton))
        self.zoomMenu.add_command(label="-25%",command = lambda: self.browserView.zoomOut(self.zoomMenu,self.zoomButton))

        self.browserView.browser.bind("<<DownloadingResource>>",self.pageChanged) # Bind link clicked event to pageChanged method
        self.browserView.browser.bind("<<DoneLoading>>",self.loadingDone) # Bind page loaded event to loadingDone method
        self.browserView.browser.bind("<<TitleChanged>>",self.changeTabTitle) # Bind URL changed event to pageChanged method
        
        self.goToPage(page = startpage)

    def goToPage(self,event=None,page = None, doNotAddToSessionHistory = False): #Handle going to pages
        if page == None:
            page = self.addressBar.get()
        self.setAddressBar(page) # Set the address bar to the new URL
        if not doNotAddToSessionHistory:
            self.AddToSessionHistory()
        print(page)
        if page != "flamingearth://newtab":
            try:
                self.newtab.newTabFrame.pack_forget()
            except Exception:
                print("newtab frame did not need to be destroyed")
        if page[:4] == "http" or page[:4] == "file" or page[:5] == "about":
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
                self.settingsFrame.settings_frame.pack_forget()
            elif subpage == "settings":
                self.newtab.newTabFrame.pack_forget()
                self.settingsFrame.settings_frame.pack(fill="both", expand=True)
            self.refreshButton.configure(text = "↺")

    def pageChanged(self,event=None):
        oldUrl = self.currentAddress.get()
        newURL = self.browserView.browser.current_url
        print("[TABFRAME] Page changed to:",newURL)
        self.setAddressBar(newURL) # Set the address bar to the new URL
        if (not self.doNotClearForwardHistory) and oldUrl != newURL:    
            self.ClearForwardHistory()
            self.backbutton.configure(state="normal") # Enable back button     
            self.AddToSessionHistory()
        
    def setAddressBar(self,page):
        self.currentAddress.set(page)
        self.addressBar.update()
        self.refreshButton.configure(text = "X")
    
    def loadingDone(self,event=None):
        print(self.sessionUrls)
        fileHandler.history.append(self.browserView.browser.current_url)
        fileHandler.historyTimeAccessed.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.refreshButton.configure(text = "↺")
        self.refreshButton.update()
        self.changeTabTitle(None,True, self.browserView.browser.title) # Change the tab title to the current page title
        print("[TABFRAME] Finished loading")

    def changeTabTitle(self,event, IsFromCustomProtocol = False, CustomTitle = "Tab title"):
        print("[TabFrame] Tab title event given")
        if not IsFromCustomProtocol:
            self.tabTitle = self.browserView.browser.title # Get the current title from the browser
        else :
            self.tabTitle = CustomTitle
        self.tabFrame.event_generate("<<TabTitleChanged>>") # Trigger the event with the new title
    
    def goHome(self,event=None):
        self.goToPage(page = self.homepage)
        self.ClearForwardHistory()
    
    def back(self,event=None):
        self.goToPage(page = self.sessionUrls[self.sessionBacks],doNotAddToSessionHistory=True)
        print(self.sessionBacks, " ", self.sessionUrls[self.sessionBacks])
        self.sessionBacks -= 1
        self.forwardbutton.configure(state="normal") # Enable forward button
        if abs(self.sessionBacks) >= len(self.sessionUrls):
            self.backbutton.configure(state="disabled")
            self.backbutton.update()

    def forward(self,event=None):
        self.goToPage(page = self.sessionUrls[self.sessionBacks + 2],doNotAddToSessionHistory=True)
        print(self.sessionBacks + 2, " ", self.sessionUrls[self.sessionBacks + 2])
        self.sessionBacks += 1
        if self.sessionBacks <= -2:
            self.backbutton.configure(state="normal")
            self.backbutton.update()
            self.forwardbutton.configure(state="disabled")
            self.forwardbutton.update()

    def ClearForwardHistory(self):
        forwardHistoryPoint =len(self.sessionUrls)+self.sessionBacks+1
        print("[TabFrame] Forward History Point ", forwardHistoryPoint)
        ## self.sessionUrls = self.sessionUrls[:forwardHistoryPoint]
        self.sessionBacks = -2
        self.forwardbutton.configure(state="disabled")
        self.forwardbutton.update()
        print("[TabFrame] Forward history cleared")

    def AddToSessionHistory(self):
        self.sessionUrls.append(self.addressBar.get())
        self.sessionTitles.append(self.tabTitle)
        print("[TabFrame] Added to session history:", self.browserView.browser.current_url)
        if self.sessionBacks != -2:
            self.backbutton.configure(state="normal")
            self.backbutton.update()