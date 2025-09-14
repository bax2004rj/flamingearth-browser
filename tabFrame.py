import tkinter
from tkinter import ttk, messagebox
import datetime
import newTab
import browserTab
import settings
import fileHandler
import history
import bookmarks
from PIL import Image, ImageTk as ImageTK
import urllib.request
import subprocess
import sys
import os
import threading

class newFrame:
    def __init__(self,tabFrame,frameVar,historyMenu,startpage="flamingearth://newtab",tabid=0,saveHistory=True):
        self.homepage = startpage
        self.sessionTitles = []
        self.sessionUrls = []

        self.historyItems = [] #History items built on pre-sorted list, but also ocntaining titles
    
        self.sessionBacks = tkinter.IntVar(tabFrame,-2)
        self.sessionMenuNumber = tkinter.IntVar(tabFrame, 0)
        self.doNotClearForwardHistory = False
        self.saveHistory = saveHistory
        self.tab_id = tabid
        self.tabFrame = tabFrame
        self.tabTitle = "New Tab         "
        self.tabIconURL = None
        self.iconFile = fileHandler.noIcon
        self.tabIcon = ImageTK.PhotoImage(file=self.iconFile)

        self.historyGrabber = threading.Thread(target=self.loadHistoryObjects)
        self.historyGrabber.start()

        self.addressObject = tkinter.Frame(tabFrame)
        self.addressObject.pack(side = "top",fill = "x")
        
        self.currentAddress = tkinter.StringVar(tabFrame,value = startpage)

        self.backbutton = ttk.Button(self.addressObject,text = "←",command = lambda: self.back())
        self.backbutton.pack(side = "left")
        self.forwardbutton = ttk.Button(self.addressObject,text = "→",command = lambda: self.forward())
        self.forwardbutton.pack(side = "left")
        self.backbutton.configure(state="disabled") # Disable back button
        self.forwardbutton.configure(state="disabled")

        self.backMenu = tkinter.Menu(self.addressObject)
        self.backbutton.bind("<Button-3>",self.showBackMenu)
        self.forwardbutton.bind("<Button-3>",self.showBackMenu)

        self.addressBar = ttk.Combobox(self.addressObject,textvariable = self.currentAddress,values = self.historyItems)
        self.addressBar.bind("<<ComboboxSelected>>",self.convertAndGo)
        self.addressBar.bind("<Return>",self.goToPage)
        self.addressBar.pack(fill = "x")

        self.historyMenu = historyMenu

        self.downloadMenu = tkinter.Menu(self.addressBar)
        self.downloadMenu.add_command(label="Clear downloads")

        self.zoomMenu = tkinter.Menu(self.addressBar)

        self.bookmarksMenu = tkinter.Menu(self.addressBar)

        self.hamburgerMenu = tkinter.Menu(self.addressBar)

        self.newtab = newTab.newTab(tabFrame,frameVar,startpage)
        self.browserView = browserTab.newTab(tabFrame,self.zoomMenu,self.back,self.forward)
        self.settingsFrame = settings.Settings(tabFrame)
        self.historyFrame = history.History(tabFrame)
        self.bookmarksFrame = bookmarks.Bookmarks(tabFrame)

        self.menuButton = ttk.Menubutton(self.addressBar,text = "≡",menu = self.hamburgerMenu)
        self.menuButton.pack(side = "right")

        self.downloadButton = ttk.Menubutton(self.addressBar,text = "↓",menu = self.downloadMenu)
        self.downloadButton.pack(side = "right")

        self.zoomButton = ttk.Menubutton(self.addressBar,text = "🔍",menu = self.zoomMenu, state="disabled")

        self.homeButton = ttk.Button(self.addressBar,text = "⌂️",command = self.goHome)
        self.homeButton.pack(side = "right")

        self.refreshButton = ttk.Button(self.addressBar,text = "↺",command= self.browserView.refresh)
        self.refreshButton.pack(side="right")

        self.addBookmarkButton = ttk.Button(self.addressBar,text="☆",command=lambda:self.bookmarksFrame.addBookmark(self.addressBar.get(),self.tabTitle,self.tabIconURL))
        self.addBookmarkButton.pack(side="right")

        ##self.gobutton = ttk.Button(self.addressBar,style="Accent.TButton",text = "Go",command=self.goToPage)
        ##self.gobutton.pack(side="right")

        self.hamburgerMenu.add_command(label="New tab")
        self.hamburgerMenu.add_command(label="New window")
        self.hamburgerMenu.add_separator()
        self.hamburgerMenu.add_cascade(label="History",menu=self.historyMenu)
        self.hamburgerMenu.add_cascade(label="Downloads",menu=self.downloadMenu)
        self.hamburgerMenu.add_cascade(label="Bookmarks",menu=self.bookmarksMenu)
        self.hamburgerMenu.add_separator()
        self.hamburgerMenu.add_command(label="Find",command=self.browserView.toggleFindBar, state="disabled")
        self.hamburgerMenu.add_cascade(label="Zoom",menu=self.zoomMenu)
        self.hamburgerMenu.add_command(label="Settings",command=lambda: self.goToPage(page = "flamingearth://settings"))

        self.zoomMenu.add_command(label="Zoom level: 100%",state="disabled") # When creating the menu entry, do NOT set state="disabled"
        self.zoomMenu.add_separator()
        self.zoomMenu.add_command(label="+25%",command = lambda: self.browserView.zoomIn(self.zoomMenu,self.zoomButton))
        self.zoomMenu.add_command(label="Reset",command = lambda: self.browserView.zoomReset(self.zoomMenu,self.zoomButton))
        self.zoomMenu.add_command(label="-25%",command = lambda: self.browserView.zoomOut(self.zoomMenu,self.zoomButton))

        self.browserView.browser.bind("<<DownloadingResource>>",self.pageChanged) # Bind link clicked event to pageChanged method
        self.browserView.browser.bind("<<DoneLoading>>",self.loadingDone) # Bind page loaded event to loadingDone method
        self.browserView.browser.bind("<<TitleChanged>>",self.changeTabTitle) # Bind URL changed event to pageChanged method

        self.historyFrame.history_list.bind("<<HistoryURLClicked>>", self.historyClicked) # Bind history URL clicked event to goToPage method
        self.historyFrame.history_list.bind("<<DoneLoading>>",lambda e:self.loadingDone(fromFlamingearthProtocol=True)) # Bind history loaded event to loadingDone method

        self.newtab.newTabFrame.bind("<<URLChanged>>",self.newTabClick)

        self.goToPage(page = startpage)

    def convertAndGo(self,event=None): #Take in combobox input when quick item selected and go to page
        item = self.addressBar.get()
        index = self.historyItems.index(item)
        self.addressBar.set(fileHandler.historyRanked[index])
        self.goToPage()

    def goToPage(self,event=None,page = None, doNotAddToSessionHistory = False, doNotAddToHistory = False,reloading = False): #Handle going to page
        if page == None:
            page = self.addressBar.get()
        self.setAddressBar(page) # Set the address bar to the new URL
        self.historyFrame.isEnabled = False # Set if history should load items
        if not doNotAddToSessionHistory:
            self.AddToSessionHistory()
        print(page)
        protocol = page.split(":")[0]
        urlSplit = page.split(".")
        print(protocol)
        if page[:12] != "flamingearth://newtab":
            try:
                self.newtab.newTabFrame.pack_forget()
                self.settingsFrame.settings_frame.pack_forget()
                self.historyFrame.history_frame.pack_forget()
            except Exception:
                print("Flamingearth protocol frame did not need to be destroyed")
        if protocol == "http" or protocol == "https" or protocol == "file" or protocol == "about":
            try:
                self.browserView.showBrowserView()
                self.zoomButton.configure(state="normal") # Enable zoom menu
                self.hamburgerMenu.entryconfig("Find", state="normal") # Enable find menu
            except Exception:
                pass   
            self.browserView.changeUrl(page,force=reloading)
            self.zoomButton.configure(state="disabled") # Disable zoom menu
        elif protocol == "flamingearth":
            subpage = page.split("/")
            print(subpage)
            self.browserView.hideBrowserView()
            self.hamburgerMenu.entryconfig("Find", state="disabled") # Disable find menu
            self.zoomButton.configure(state="disabled") # Disable zoom menu
            if subpage[2] == "newtab":
                self.newtab.newTabFrame.pack(fill="both", side="top", expand=True)
                self.settingsFrame.settings_frame.pack_forget()
                self.historyFrame.history_frame.pack_forget()
                self.bookmarksFrame.bookmarks_frame.pack_forget()
                self.tabTitle = "New Tab"
                self.loadingDone(fromFlamingearthProtocol=True)
            elif subpage[2] == "settings":
                self.newtab.newTabFrame.pack_forget()
                self.settingsFrame.settings_frame.pack(fill="both", side="top", expand=True)
                self.historyFrame.history_frame.pack_forget()
                self.bookmarksFrame.bookmarks_frame.pack_forget()
                self.tabTitle = "Settings"
                self.loadingDone(fromFlamingearthProtocol=True)
            elif subpage[2] == "history":
                self.newtab.newTabFrame.pack_forget()
                self.settingsFrame.settings_frame.pack_forget()
                self.bookmarksFrame.bookmarks_frame.pack_forget()
                self.historyFrame.history_frame.pack(fill="both", side="top", expand=True)
                self.tabTitle = "History"
                self.historyFrame.load_history()
                self.historyFrame.isEnabled = True
                try:
                    if subpage[3] == "clear" or subpage[3] == "delete":
                        self.historyFrame.clear_history()
                    if subpage[3].startswith("search?q="):
                        searchTemp = subpage[3].split("\"")[1:]
                        search=""
                        for i in searchTemp:
                            search += i
                        self.historyFrame.searchText.set(search)
                        self.historyFrame.search_bar.configure(textvariable = self.historyFrame.searchText)
                        self.historyFrame.search()
                except IndexError:
                    print("[TabFrame] No subpages requested")
            elif subpage[2] == "bookmarks":
                self.newtab.newTabFrame.pack_forget()
                self.settingsFrame.settings_frame.pack_forget()
                self.historyFrame.history_frame.pack_forget()
                self.bookmarksFrame.bookmarks_frame.pack(fill="both", side="top", expand=True)
                self.tabTitle = "Bookmarks"
                self.bookmarksFrame.loadTreeview()
                try:
                    if subpage[3].startswith("search?q="):
                        searchTemp = subpage[3].split("\"")[1:]
                        search=""
                        for i in searchTemp:
                            search += i
                        self.bookmarksFrame.searchText.set(search)
                        self.bookmarksFrame.search_bar.configure(textvariable = self.historyFrame.searchText)
                        self.bookmarksFrame.search()
                    # TODO: Add subfolder handling
                except IndexError:
                    print("[TabFrame] No subpages requested")
                    self.bookmarksFrame.load_bookmarks()
                    self.bookmarksFrame.isEnabled = True
            else:
                self.tabTitle = "Error"
                self.newtab.newTabFrame.pack_forget()
                self.settingsFrame.settings_frame.pack_forget()
                self.historyFrame.history_frame.pack_forget()
                self.bookmarksFrame.bookmarks_frame.pack_forget()
                self.browserView.showBrowserView()
                self.browserView.browser.show_error_page(page,f"{subpage} is not recognized as a valid flamingearth:// URL. Check spelling and try again","404")
        elif protocol is not None and ":" in page:
            messageboxOut = messagebox.askokcancel("Confirm URL open", f"The URL \"{page}\" will open in another app. Would you like to continue?")
            if messageboxOut and sys.platform.startswith("linux"):
                try:
                    subprocess.Popen(["xdg-open",page])
                except Exception as e:
                    print(f"[TabFrame] Failed to open, gave exception {e}")
            elif messageboxOut and os.name == "nt":
                os.startfile(page)
            elif messageboxOut and sys.platform.startswith("darwin"):
                try:
                    subprocess.Popen(["open",page])
                except Exception as e:
                    print(f"[TabFrame] Failed to open, gave exception {e}")
            self.goToPage(page=self.sessionUrls[-2])
        elif len(urlSplit)>=2 or len(urlSplit)<=4 and ":" not in page: #Add https:// in front of url without protocol
            self.goToPage(page="https://"+page,reloading=reloading)
        else: # If it failed everything else, its probably a search query
            self.goToSearchEngine(page)
        self.refreshButton.configure(text = "↺")
        self.tabFrame.event_generate("<<TabTitleChanged>>")

    def goToSearchEngine(self,page):
        urlFriendlySearchQuery = page.replace(" ",fileHandler.searchEngineDefaultSpaceReplacer)
        self.goToPage(page = fileHandler.searchEngine + urlFriendlySearchQuery)

    def pageChanged(self,event=None):
        oldUrl = self.currentAddress.get()
        newURL = self.browserView.browser.current_url
        print("[TABFRAME] Page changed to:",newURL)
        self.setAddressBar(newURL) # Set the address bar to the new URL
        if (not self.doNotClearForwardHistory) and oldUrl != newURL:    
            self.ClearForwardHistory()
            self.backbutton.configure(state="normal") # Enable back button     
            self.AddToSessionHistory()

    def newTabClick(self,event=None):
        url = self.newtab.chosenURL
        print("[TABFRAME] New Tab URL clicked:", url)
        self.goToPage(page=url)

    def historyClicked(self,event=None):
        historyURL = self.historyFrame.historyURL
        print("[TABFRAME] History URL clicked:", historyURL)
        self.goToPage(page=historyURL, doNotAddToSessionHistory=False, doNotAddToHistory=False)
        
    def setAddressBar(self,page):
        print("Updating page")
        self.currentAddress.set(page)
        self.addressBar.update()
        self.refreshButton.configure(text = "X")
    
    def loadingDone(self,event=None,fromFlamingearthProtocol=False):
        print(self.sessionUrls)
        try:
            latestHistoryItem = fileHandler.historyURL[-1]
        except IndexError:
            latestHistoryItem = ''
        if self.saveHistory and latestHistoryItem != self.browserView.browser.current_url:
            fileHandler.historyURL.append(self.browserView.browser.current_url)
            fileHandler.historyTitles.append(self.tabTitle)
            fileHandler.historyIcons.append(self.iconFile)
            fileHandler.historyTimeAccessed.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.refreshButton.configure(text = "↺")
        self.browserView.loading = False
        if not fromFlamingearthProtocol:
            self.changeTabTitle(None,True, self.browserView.browser.title) # Change the tab title to the current page title
        self.doNotClearForwardHistory = False # Reset the doNotClearForwardHistory flag
        if not self.doNotClearForwardHistory and len(self.sessionUrls)> len(self.sessionTitles):
            self.finishAddingToSessionHistory()
        print("[TABFRAME] Finished loading")

    def changeTabTitle(self,event, IsFromCustomProtocol = False, CustomTitle = "Tab title", customIcon = fileHandler.noIcon): #Update tab titles. Custom icon should be a string containing a location where the icon is (usually supplied by fileHandler)
        print("[TabFrame] Tab title event given")
        newTabTitle = self.browserView.browser.title
        if (not IsFromCustomProtocol) and newTabTitle != self.tabTitle:
            self.tabTitle =  newTabTitle# Get the current title from the browser
            self.tabIconURL = self.browserView.browser.icon # Get the current icon from the browser        
            if not self.tabIconURL == None:
                try:
                    self.image_data = urllib.request.urlopen(self.tabIconURL).read()
                    self.iconFile = fileHandler.saveIcon(self.image_data)
                    self.tabIcon = ImageTK.PhotoImage(file=self.iconFile)
                    print("[TabFrame] New icon set successfully")
                except Exception as e:
                    print("[TabFrame] Error loading icon from URL:", e)
                    self.iconFile = fileHandler.noIcon
                    self.tabIcon = ImageTK.PhotoImage(file=fileHandler.noIcon)
            else:
                self.iconFile = fileHandler.noIcon
                self.tabIcon = ImageTK.PhotoImage(file=fileHandler.noIcon)
                print("[TabFrame] Tab icon URL not set")
        elif IsFromCustomProtocol:
            self.tabTitle = CustomTitle
            self.iconFile = customIcon
            self.tabIcon = ImageTK.PhotoImage(file=self.iconFile)
        else:
            print("[TabFrame] Tab title did not need to update")
        self.tabFrame.event_generate("<<TabTitleChanged>>") # Trigger the event with the new title

    def goHome(self,event=None):
        self.goToPage(page = self.homepage)
        self.ClearForwardHistory()
    
    def back(self,event=None):
        sessionBacks = self.sessionBacks.get()
        self.goToPage(page = self.sessionUrls[sessionBacks],doNotAddToSessionHistory=True)
        print(sessionBacks, " ", self.sessionUrls[sessionBacks])
        self.sessionBacks.set(sessionBacks - 1)
        self.forwardbutton.configure(state="normal") # Enable forward button
        self.doNotClearForwardHistory = True # Do not clear forward history when going back
        if abs(sessionBacks) >= len(self.sessionUrls):
            self.backbutton.configure(state="disabled")
            self.backbutton.update()

    def forward(self,event=None):
        sessionBacks = self.sessionBacks.get()
        self.goToPage(page = self.sessionUrls[sessionBacks + 2],doNotAddToSessionHistory=True)
        print(sessionBacks + 2, " ", self.sessionUrls[sessionBacks + 2])
        self.sessionBacks.set(sessionBacks + 1)
        self.doNotClearForwardHistory = True
        if sessionBacks >= -3:
            self.backbutton.configure(state="normal")
            self.backbutton.update()
            self.forwardbutton.configure(state="disabled")
            self.forwardbutton.update()
        if abs(sessionBacks) <= len(self.sessionUrls):
            self.backbutton.configure(state="normal")
            self.backbutton.update()

    def ClearForwardHistory(self):
        sessionBacks = self.sessionBacks.get()
        forwardHistoryPoint =len(self.sessionUrls)+sessionBacks+2
        print("[TabFrame] Forward History Point ", forwardHistoryPoint)
        self.sessionUrls = self.sessionUrls[:forwardHistoryPoint]
        self.sessionBacks.set(-2)
        self.sessionMenuNumber.set(len(self.sessionTitles)-1)
        self.forwardbutton.configure(state="disabled")
        self.forwardbutton.update()
        self.backMenu.delete(0, 'end')  # Clear and add all items to the back menu
        try:
            for i in range(len(self.sessionUrls)):
                self.backMenu.add_radiobutton(label=self.sessionTitles[i], command=self.jumpToPage, variable=self.sessionMenuNumber, value=i)
        except IndexError:
            print("[TabFrame] No session URLs to clear")
        print("[TabFrame] Forward history cleared")

    def AddToSessionHistory(self):
        sessionBacks = self.sessionBacks.get()
        self.sessionUrls.append(self.addressBar.get())
        print("[TabFrame] Added URL to session history:", self.browserView.browser.current_url)
        if abs(sessionBacks) <= len(self.sessionUrls):
            self.backbutton.configure(state="normal")
            self.backbutton.update()

    def finishAddingToSessionHistory(self):
        self.sessionTitles.append(self.tabTitle)
        self.backMenu.add_radiobutton(label=self.tabTitle, command=self.jumpToPage, variable=self.sessionMenuNumber,value = self.sessionTitles.index(self.tabTitle))
        self.sessionMenuNumber.set(len(self.sessionTitles)-1) # Set the current session menu number to the last item
        print("[TabFrame] Finished adding to session history:", self.sessionTitles[-1], " ", self.sessionUrls[-1])

    def showBackMenu(self,event):
        try:
            self.backMenu.tk_popup(event.x_root,event.y_root,0)
        finally:
             self.backMenu.grab_release()

    def jumpToPage(self):
        sessionBacks = self.sessionMenuNumber.get()
        self.goToPage(page = self.sessionUrls[sessionBacks],doNotAddToSessionHistory=True)
        print(sessionBacks, " ", self.sessionUrls[sessionBacks])
        self.doNotClearForwardHistory = True # Do not clear forward history when going back
        if sessionBacks >= -2:
            self.backbutton.configure(state="normal")
            self.backbutton.update()
            self.forwardbutton.configure(state="disabled")
            self.forwardbutton.update()
        if abs(sessionBacks) <= len(self.sessionUrls):
            self.backbutton.configure(state="normal")
            self.backbutton.update()
        if abs(sessionBacks) >= len(self.sessionUrls):
            self.backbutton.configure(state="disabled")
            self.backbutton.update()
        self.sessionBacks.set(0-(len(self.sessionTitles)-self.sessionMenuNumber.get()))

    def loadHistoryObjects(self):
        for item in fileHandler.historyRanked:
            originalIndex = fileHandler.historyURL.index(item)
            self.historyItems.append(f"{fileHandler.historyTitles[originalIndex]} ({item})")
