import tkinter
from tkinter import ttk
import sv_ttk
# Other imports
import tabFrame
import customTab

class main():
    def __init__(self):
        self.app = tkinter.Tk()
        self.app.winfo_toplevel().title("Flamingearth Browser v1.0a")
        self.app.geometry("1366x720")

        sv_ttk.set_theme("dark") # Enable darkmode

        self.tabs = customTab.customTab(self.app) # Create tabs
        self.tabs.pack(fill="both",expand=1)
        self.tabs.bind_newtab(self.tabAdd)

        self.tabObjects = []
        self.tabFrames = []
        self.tabVars = []
        self.homepage = "flamingearth://newtab"
    
    def tabAdd(self,page = "http://www.google.com/"): # Create new tab in tabFrame module
        newFrame = ttk.Frame(self.tabs)
        newtab = self.tabs.add(newFrame,text="New tab")
        self.tabVars.append(tkinter.StringVar(self.app,"New tab"))
        self.tabFrames.append(newFrame)
        self.tabObjects.append(newtab) # Formerly textVariable = self.tabVars[-1]
        self.tabFrame = tabFrame.newFrame(self.tabFrames[-1],self.tabVars[-1],self.homepage)
        print ("New tab generated")
        

browser = main()
browser.tabAdd()
browser.app.mainloop()