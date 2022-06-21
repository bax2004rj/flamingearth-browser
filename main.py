import tkinter
from tkinter import ttk
import sv_ttk
# Other imports
import customTab
import browserTab

class main():
    def __init__(self):
        self.app = tkinter.Tk()
        self.app.winfo_toplevel().title("Flamingearth Browser v1.0a")
        self.app.geometry("1366x720")

        sv_ttk.set_theme("dark") # Enable darkmode

        self.addcloseframe = ttk.Frame(self.app)
        self.addcloseframe.pack(side="top", fill = "x")

        self.newTab = ttk.Button(self.addcloseframe,text="+",command= self.tabAdd) # Tab adder
        self.newTab.pack(side="right")

        self.tabs = customTab.customTab(self.app) # Create tabs
        self.tabs.pack(fill="both",expand=1)

        self.tabObjects = []
        self.tabFrames = []
        self.tabVars = []
    
    def tabAdd(self,page = "http://www.google.com/"): # Create new tab in browserTab module
        newFrame = ttk.Frame(self.tabs)
        newTab = self.tabs.add(newFrame,text="New tab")
        self.tabVars.append(tkinter.StringVar(self.app,"New tab"))
        self.tabFrames.append(newFrame)
        self.tabObjects.append(newTab) # Formerly textVariable = self.tabVars[-1]
        print ("New tab generated")
        browserTab.newTab(self.tabFrames[-1],self.tabVars[-1],page)

browser = main()
browser.tabAdd()
browser.app.mainloop()