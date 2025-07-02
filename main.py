import tkinter
from tkinter import ttk
import sv_ttk
# Other imports
import tabFrame
import customTab
import fileHandler

class main():
    def __init__(self):
        fileHandler.loadSettings() # Read settings from file
 
        self.app = tkinter.Tk()
        self.setDarkmode() # Set dark mode
        self.app.winfo_toplevel().title("Flamingearth Browser v1.0a")
        self.app.geometry("1366x720")
       

        self.tabs = customTab.customTab(self.app) # Create tabs
        self.tabs.pack(fill="both",expand=1)
        self.tabs.bind_newtab(self.tabAdd)

        self.tabObjects = []
        self.tabFrames = []
        self.tabVars = []
        self.tabProcesses = []
        self.processCount = 0 
        self.homepage = "flamingearth://newtab"
        self.app.bind("<<TabTitleChanged>>",self.tabEdit)
        self.app.bind("<<NotebookTabClosed>>",self.checkToQuit)

    def setDarkmode(self):
        if fileHandler.darkmode == True and fileHandler.tkinterTheme == "sv_ttk":
            sv_ttk.set_theme("dark") # Enable darkmode
        elif fileHandler.darkmode == False and fileHandler.tkinterTheme == "sv_ttk":
            sv_ttk.set_theme("light") # Enable lightmode
        
    def tabAdd(self,page = "http://www.google.com/"): # Create new tab in tabFrame module
        newFrame = ttk.Frame(self.tabs)        
        self.processCount += 1
        newtab = self.tabs.add(newFrame,text="New tab") # Add new tab to the notebook
        self.tabVars.append(tkinter.StringVar(self.app,"New tab"))
        self.tabFrames.append(newFrame)
        self.tabObjects.append(newtab) # Formerly textVariable = self.tabVars[-1]
        self.tabProcesses.append(tabFrame.newFrame(self.tabFrames[-1],self.tabVars[-1],self.homepage,self.processCount))

        print ("New tab generated (process id: %d)"% self.processCount)

    def tabEdit(self,event):
        try:
            ##event.widget.newTitle
            frameID=self.tabFrames.index(event.widget)
            print(frameID)
            newTitle = self.tabProcesses[frameID].tabTitle
            self.tabs.tab(event.widget, text=newTitle)  # event.data[0] is the new title
            self.tabs.update()
            print("[Main] Tab title successfully edited")
        except Exception as e:
            print(f"[Main] Error editing tab title: {e}")
    
    def checkToQuit(self,event):
        print("[Main] Tab closed event received")
        if len(self.tabs.tabs()) == 0:
            self.app.quit()
        else:
            print("[Main] There are ", len(self.tabs.tabs()), " tabs remaining")
browser = main()
browser.tabAdd()
browser.app.mainloop()