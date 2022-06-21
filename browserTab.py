import tkinter
from tkinter import ttk
from tkinterweb import HtmlFrame

crashHandling = True

class newTab():
    def __init__(self,tab,stringVar,startpage):
        self.addressObject = tkinter.Frame(tab)
        self.addressObject.pack(side = "top",fill = "x")
        
        self.currentAddress = tkinter.StringVar(tab,value = startpage)

        self.addressBar = ttk.Entry(self.addressObject,textvariable = self.currentAddress)
        self.addressBar.bind("<Return>",self.goToPage)
        self.addressBar.pack(fill = "x")

        self.gobutton = ttk.Button(self.addressBar,style="Accent.TButton",text = "Go")
        self.gobutton.pack(side="right")

        self.browser = HtmlFrame(tab)
        self.browser.pack(fill="both", expand=True)

        self.browser.enable_crash_prevention(isenabled=crashHandling)
        self.browser.load_website(startpage)

    def goToPage(self,event = None):
        page = self.currentAddress.get()
        self.browser.load_website(page)