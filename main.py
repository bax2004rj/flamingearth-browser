import tkinter
from tkinter import ttk
import tkinter.messagebox
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
        self.app.winfo_toplevel().title("Flamingearth Browser v1.0a")
        self.app.geometry("1366x720")
       
        self.reversedHistoryItems = list(reversed(fileHandler.historyTitles))
        self.historyMenuImages = []
        self.historyMenu = tkinter.Menu(self.app)
        for i in range(10):
            try:
                url = fileHandler.historyURL[len(fileHandler.historyURL)-i-1]
                self.historyMenuImages.append(ImageTK.PhotoImage(Image.open(fileHandler.historyIcons[len(fileHandler.historyURL)-i-1]).resize([16,16])))
                self.historyMenu.add_command(label=self.reversedHistoryItems[i],command=lambda:self.goToPage(page=url),image=self.historyMenuImages[i])
                ##print(self.reversedHistoryItems[i])
            except IndexError:
                break
        self.historyMenu.add_separator()
        self.historyMenu.add_command(label="View history", command=lambda: self.goToPage(page = "flamingearth://history"))
        self.historyMenu.add_command(label="Clear history")
        self.addMenu()

        self.tabs = customTab.customTab(self.app) # Create tabs
        self.tabs.pack(fill="both",expand=1)
        self.tabs.bind_newtab(self.tabAdd)

        self.tabImage = ImageTK.PhotoImage(file=fileHandler.noIcon) # Default tab icon
        self.tabObjects = []
        self.tabFrames = []
        self.tabVars = []
        self.tabProcesses = []
        self.processCount = 0 
        self.homepage = "flamingearth://newtab"
        self.app.bind("<<TabTitleChanged>>",self.tabEdit)
        ##self.app.bind("<<NotebookTabClosed>>",self.checkToQuit)
        self.tabs.bind_close(self.checkToQuit)
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
            self.fileMenu.add_command(label="Open file")
            self.fileMenu.add_command(label="Open location")
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label="Close tab")
            self.fileMenu.add_command(label="Close window",command=self.onQuit)

            self.editMenu = tkinter.Menu(self.app)
            self.editMenu.add_command(label="Undo")
            self.editMenu.add_command(label="Redo")
            self.editMenu.add_separator()
            self.editMenu.add_command(label="Cut")
            self.editMenu.add_command(label="Copy")
            self.editMenu.add_command(label="Paste")
            self.editMenu.add_separator()
            self.editMenu.add_command(label="Find in page")

            self.viewMenu = tkinter.Menu(self.app)
            self.viewMenu.add_command(label="Zoom in")
            self.viewMenu.add_command(label="Zoom out")
            self.viewMenu.add_command(label="Reset zoom")
            self.viewMenu.add_separator()
            self.viewMenu.add_command(label="Reload/stop page")

            self.bookmarksMenu = tkinter.Menu(self.app)

            self.tabsMenu = tkinter.Menu(self.app)
            self.tabsMenu.add_command(label="New Tab",command=self.tabAdd)
            self.tabsMenu.add_command(label="Close Tab")

            self.helpMenu = tkinter.Menu(self.app)
            self.helpMenu.add_command(label = "Flamingearth Help")
            self.helpMenu.add_command(label = "About Flamingearth")

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
        newtab = self.tabs.add(newFrame,text="New Tab",image=self.tabImage,compound="left") # Add new tab to the notebook
        self.tabVars.append(tkinter.StringVar(self.app,"New Tab"))
        self.tabFrames.append(newFrame)
        self.tabObjects.append(newtab) # Formerly textVariable = self.tabVars[-1]
        self.tabProcesses.append(tabFrame.newFrame(self.tabFrames[-1],self.tabVars[-1],self.historyMenu,self.homepage,self.processCount)) #Future TODO: Open in thread

        print ("New tab generated (process id: %d)"% self.processCount)

    def tabEdit(self,event):
        try:
            ##event.widget.newTitle
            frameID=self.tabFrames.index(event.widget)
            print(frameID)
            newTitle = self.tabProcesses[frameID].tabTitle
            newIcon = self.tabProcesses[frameID].tabIcon
            print(newIcon)
            self.tabs.tab(event.widget, text=newTitle, image = newIcon)  # event.data[0] is the new title
            self.tabs.update()
            print("[Main] Tab title successfully edited")
        except Exception as e:
            print(f"[Main] Error editing tab title: {e}")

    def goToPage(self,page): #Communicate to actiely selected tab it should go somewhere.
        print(f"[Main] User requested to go to {page}")
        currentTab=self.tabs.index(self.tabs.select())
    
    def checkToQuit(self,event,index):
        print("[Main] Tab closed event received")
        self.tabProcesses[index].browserView.quitHover()
        ##time.sleep(0.1) #Delay quitting to make sure hover detection has enough to do its last check
        if len(self.tabs.tabs())-1 == 0:
            self.app.quit()
        else:
            print("[Main] There are ", len(self.tabs.tabs()), " tabs remaining")

    def onQuit(self):
        print ("Exiting...")
        openTabs = len(self.tabs.tabs())
        if fileHandler.notifyForTabsOnQuit != -1 and openTabs >= fileHandler.notifyForTabsOnQuit:
            continueClosing = tkinter.messagebox.askyesno("Confirm close", f"There are still {openTabs} tabs open. Are you sure you want to continue closing?")
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