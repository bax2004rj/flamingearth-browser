import tkinter
from tkinter import ttk, messagebox, filedialog
import sv_ttk
import darkdetect
# Other imports
import tabFrame
import customTab
import fileHandler
import os
import time
import sys
from PIL import Image, ImageTk as ImageTK
import threading
# OS specific imports
if os.name == 'nt':
    import pywinstyles,sys

class main():
    def __init__(self):
        fileHandler.loadSettings() # Read settings from file
        fileHandler.loadHistory() # Read history from file
        fileHandler.loadBookmarks() # Read bookmarks from file
        fileHandler.loadDownloads() # Read downloads from file
    
        self.app = tkinter.Tk()
        self.setDarkmode() # Set dark mode
        self.app.winfo_toplevel().title("New Tab | Flamingearth Browser v1.0a")
        self.app.geometry("1366x720")
        self.displayScaling = self.app.tk.call("tk","scaling")-(1/3)
        print(f"[MAIN] Display is scaled to {self.displayScaling*100}%")

        self.reversedHistoryItems = list(reversed(fileHandler.historyTitles))
        self.historyMenuImages = []
        self.historyMenu = tkinter.Menu(self.app)
        for i in range(10):
            try:
                url = fileHandler.historyURL[len(fileHandler.historyURL)-i-1]
                self.historyMenuImages.append(ImageTK.PhotoImage(Image.open(fileHandler.historyIcons[len(fileHandler.historyURL)-i-1]).resize([16,16])))
                self.historyMenu.add_command(label=self.reversedHistoryItems[i],command=lambda url=url: self.goToPage(page=url),image=self.historyMenuImages[i],compound="left")
                ##print(self.reversedHistoryItems[i])
            except IndexError:
                break
        self.historyMenu.add_separator()
        self.historyMenu.add_command(label="View history", command=lambda: self.goToPage(page = "flamingearth://history"))
        self.historyMenu.add_command(label="Clear history",command=lambda: self.goToPage(page = "flamingearth://history/delete"))
        
        self.tabsMenu = tkinter.Menu(self.app)
        self.tabsMenu.add_separator()
        self.tabsMenu.add_command(label="New Tab…",command=self.tabAdd)
        self.tabsMenu.add_command(label="Close Tab…",command=self.closeTab)

        self.addMenu()

        self.tabs = customTab.customTab(self.app) # Create tabs
        self.tabs.pack(fill="both",expand=1)
        self.tabs.setScaling(self.displayScaling)
        self.tabs.bind_newtab(self.tabAdd)
        self.tabs.bind_menubutton(self.tabsMenu)
        self.tabs.bind_close(self.checkToQuit)
        self.tabs.bind("<<NotebookTabChanged>>",self.changeTab)

        self.tabImage = ImageTK.PhotoImage(file=fileHandler.noIcon) # Default tab icon
        self.tabObjects = []
        self.tabFrames = []
        self.tabVars = []
        self.tabProcesses = []
        self.selectedTab = tkinter.StringVar(self.app,"New Tab")
        self.processCount = 0 
        self.homepage = "flamingearth://newtab"
        self.app.bind("<<TabTitleChanged>>",self.tabEdit)
        ##self.app.bind("<<NotebookTabClosed>>",self.checkToQuit)
        self.app.protocol("WM_DELETE_WINDOW",self.onQuit)

    def setDarkmode(self):
        if fileHandler.darkmode == True and fileHandler.tkinterTheme == "sv_ttk":
            sv_ttk.set_theme("dark") # Enable darkmode
        elif fileHandler.darkmode == False and fileHandler.tkinterTheme == "sv_ttk":
            sv_ttk.set_theme("light") # Enable lightmode
        if os.name == 'nt': # Set windows titlebar color to reflect dark mode (from example in sv_ttk)
            version = sys.getwindowsversion()
            if version.major == 10 and version.build >= 22000:
                pywinstyles.change_header_color(self.app,"#1c1c1c" if fileHandler.darkmode==True else "#fafafa")
            elif version.major == 10:
                pywinstyles.apply_style(self.app,"dark" if fileHandler.darkmode==True else "normal")

                self.app.wm_attributes("-alpha",0.99)
                self.app.wm_attributes("-alpha",1)
    
    def addMenu(self):
        if fileHandler.menuBar == True or sys.platform.startswith("darwin"):
            self.menu = tkinter.Menu(self.app)

            self.fileMenu = tkinter.Menu(self.app)
            self.fileMenu.add_command(label="New tab",command=self.tabAdd)
            self.fileMenu.add_command(label="New window")
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label="Open file",command=self.openFile)
            self.fileMenu.add_command(label="Open location",command=self.openLocation)
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label="Close tab",command=self.closeTab)
            self.fileMenu.add_command(label="Close window",command=self.onQuit)

            self.editMenu = tkinter.Menu(self.app)
            self.editMenu.add_separator()
            self.editMenu.add_command(label="Copy")
            self.editMenu.add_separator()
            self.editMenu.add_command(label="Find in page", command=self.find)

            self.viewMenu = tkinter.Menu(self.app)
            self.viewMenu.add_command(label="Zoom in",command=self.zoomIn)
            self.viewMenu.add_command(label="Zoom out",command=self.zoomOut)
            self.viewMenu.add_command(label="Reset zoom",command=self.zoomReset)
            self.viewMenu.add_separator()
            self.viewMenu.add_command(label="Reload/stop page",command=self.reload)
            self.viewMenu.add_separator()
            self.viewMenu.add_command(label="Back",command=self.back)
            self.viewMenu.add_command(label="Forward",command=self.forward)
            self.bookmarksMenu = tkinter.Menu(self.app)

            # Tabs menu was here. It's now in init()

            self.helpMenu = tkinter.Menu(self.app)
            self.helpMenu.add_command(label = "Flamingearth Help",command=lambda:self.goToPage("flamingearth://help"))
            self.helpMenu.add_command(label = "About Flamingearth",command=lambda:self.goToPage("flamingearth://about"))

            self.menu.add_cascade(label="File",menu = self.fileMenu)
            self.menu.add_cascade(label="Edit",menu = self.editMenu)
            self.menu.add_cascade(label="View",menu = self.viewMenu)
            self.menu.add_cascade(label="History",menu = self.historyMenu)
            self.menu.add_cascade(label="Bookmarks",menu = self.bookmarksMenu)
            self.menu.add_cascade(label="Tabs",menu = self.tabsMenu)
            self.menu.add_cascade(label="Help",menu = self.helpMenu)

            self.app.config(menu=self.menu)

    def tabAdd(self,page = "http://www.google.com/"): # Create new tab in tabFrame module
        newFrame = ttk.Frame(self.tabs)        
        self.processCount += 1
        newtab = self.tabs.add(newFrame,text="New Tab         ",image=self.tabImage,compound="left") # Add new tab to the notebook
        self.tabVars.append(tkinter.StringVar(self.app,"New Tab"))
        self.tabFrames.append(newFrame)
        self.tabObjects.append(newtab) # Formerly textVariable = self.tabVars[-1]
        self.tabProcesses.append(tabFrame.newFrame(self.tabFrames[-1],self.tabVars[-1],self.historyMenu,self.homepage,self.processCount)) #Future TODO: Open in thread
        self.tabsMenu.insert_radiobutton(self.processCount,label= "New Tab", value="New Tab",variable=self.selectedTab)
        
        totalWidth = 0
        self.tabs.updateNewTabButton()
        self.tabs.select(len(self.tabs.tabs())-1)
        print ("New tab generated (process id: %d)"% self.processCount)

    def tabEdit(self,event):
        try:
            ##event.widget.newTitle
            frameID=self.tabFrames.index(event.widget)
            print(frameID)
            newTitle = self.tabProcesses[frameID].tabTitle
            newIcon = self.tabProcesses[frameID].tabIcon
            print(newIcon)
            newTitleTruncated = newTitle
            print(len(newTitle))
            if len(newTitle)>fileHandler.tabWidth:
                newTitleTruncated = newTitle[:fileHandler.tabWidth-1]+"…"
            elif len(newTitle)<fileHandler.tabWidth:
                newTitleTruncated = newTitle.ljust(fileHandler.tabWidth-len(newTitle))
            print(newTitleTruncated)
            self.tabs.tab(event.widget, text=newTitleTruncated, image = newIcon)  # event.data[0] is the new title
            self.tabs.update()
            if self.tabsMenu.cget("tearoff")==True:  
                self.tabsMenu.entryconfig(frameID+1,label = newTitle,value=newTitleTruncated)
            else:
                self.tabsMenu.entryconfig(frameID,label = newTitle,value=newTitleTruncated)
            self.selectedTab.set(newTitle)
            self.tabs.updateNewTabButton()
            print("[Main] Tab title successfully edited")
            self.app.winfo_toplevel().title(f"{newTitle} | Flamingearth Browser v1.0a")

        except Exception as e:
            print(f"[Main] Error editing tab title: {e}")

    def changeTab(self,event):
        itemID = self.tabs.index(self.tabs.select())
        self.selectedTab.set(self.tabs.tab(itemID,"text"))

    # Menu button command bindings
    def openFile(self):
        file = "file:/" + filedialog.askopenfilename()
        self.goToPage(file)

    def openLocation(self):
        currentTab=self.tabs.index(self.tabs.select())
        self.tabProcesses[currentTab].addressBar.focus()

    def goToPage(self,page): #Communicate to actiely selected tab it should go somewhere.
        currentTab=self.tabs.index(self.tabs.select())
        print(f"[Main] User requested to go to {page}. They are on tab {currentTab}")
        self.tabProcesses[currentTab].goToPage(page=page)

    def zoomIn(self):
        currentTab=self.tabs.index(self.tabs.select())
        self.tabProcesses[currentTab].browserView.zoomIn(self.tabProcesses[currentTab].zoomMenu,self.tabProcesses[currentTab].zoomButton)
    
    def zoomOut(self):
        currentTab=self.tabs.index(self.tabs.select())
        self.tabProcesses[currentTab].browserView.zoomOut(self.tabProcesses[currentTab].zoomMenu,self.tabProcesses[currentTab].zoomButton)

    def zoomReset(self):
        currentTab=self.tabs.index(self.tabs.select())
        self.tabProcesses[currentTab].browserView.zoomReset(self.tabProcesses[currentTab].zoomMenu,self.tabProcesses[currentTab].zoomButton)

    def reload(self):
        currentTab=self.tabs.index(self.tabs.select())
        self.tabProcesses[currentTab].browserView.reload()

    def back(self):
        currentTab=self.tabs.index(self.tabs.select())
        self.tabProcesses[currentTab].back()
    
    def forward(self):
        currentTab=self.tabs.index(self.tabs.select())
        self.tabProcesses[currentTab].forward()
    
    def closeTab(self):
        currentTab=self.tabs.index(self.tabs.select())
        if self.tabs.beforeCloseFunction is not None:
            self.tabs.beforeCloseFunction(None,currentTab)
        self.tabs.forget(currentTab)
        self.tabs.updateNewTabButton()
        self.tabs.event_generate("<<NotebookTabClosed>>")

    def find(self):
        currentTab=self.tabs.index(self.tabs.select())
        self.tabProcesses[currentTab].browserView.toggleFindBar() 

    # Exit checks
    def checkToQuit(self,event,index):
        print("[Main] Tab closed event received")
        self.tabProcesses[index].browserView.quitHover()
        if len(self.tabs.tabs())-1 == 0:
            self.app.quit()
        else:
            print("[Main] There are ", len(self.tabs.tabs()), " tabs remaining")
        self.tabsMenu.delete(index)

    def onQuit(self):
        print ("Exiting...")
        openTabs = len(self.tabs.tabs())
        if fileHandler.notifyForTabsOnQuit != -1 and openTabs >= fileHandler.notifyForTabsOnQuit:
            continueClosing = messagebox.askyesno("Confirm close", f"There are still {openTabs} tabs open. Are you sure you want to continue closing?")
            if continueClosing == True:
                for i in self.tabProcesses:
                    i.browserView.quitHover()
                    print(f"[MAIN] Shut down tab {self.tabProcesses.index(i)}")
                time.sleep(0.1)
                self.app.destroy()

    def __enter__(self):
        print ("Starting browser...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        fileHandler.saveSettings()
        fileHandler.saveHistory()
        fileHandler.saveBookmarks()
        fileHandler.saveDownloads()

with main() as browser:
    browser.tabAdd()
    browser.app.mainloop()