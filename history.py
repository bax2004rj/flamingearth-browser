import tkinter
from tkinter import ttk,messagebox
import fileHandler
import sv_ttk
import os
import datetime
import humanize
import tkcalendar

class History:
    def __init__(self,tab):
        self.history_frame = ttk.Frame(tab)

        self.topbar = ttk.Frame(self.history_frame, style = "Card.TFrame")
        self.topbar.pack(side="top", fill="x")

        self.sidebar = tkinter.Frame(self.history_frame)
        self.sidebar.pack(side="left", fill="y")

        self.progress = ttk.Progressbar(self.topbar)

        self.top_label = ttk.Label(self.topbar, text="History",font=("TkDefaultFont", 16))
        self.top_label.pack(side="left", padx=10)

        self.searchFrame = ttk.Frame(self.topbar)
        self.searchFrame.pack()

        self.defaultText = tkinter.StringVar(self.searchFrame,value="Search through history…")
        self.searchText = tkinter.StringVar(self.searchFrame)
        self.search_bar = ttk.Entry(self.searchFrame,textvariable=self.defaultText)
        self.search_bar.pack(side = "left")
        self.search_bar.bind("<FocusIn>",self.enterSearch)
        self.searchText.trace_add("write",self.search)
        self.deleteButton = ttk.Button(self.searchFrame,text="⌫", style= "Accent.TButton",command=self.cancelSearch)
        self.advancedButton = ttk.Button(self.searchFrame,text="Search options",command=self.searchOptions)
        self.advancedButton.pack(side="right")

        self.errorBar = ttk.Frame(self.topbar, style = "TEntry")
        self.errorText = ttk.Label(self.errorBar,text="")
        self.errorText.pack(in_=self.errorBar, side="left", padx=10, fill = "x")
        self.errorClose = ttk.Button(self.errorBar, text="OK", style = "Accent.TButton", command=self.errorBar.pack_forget)
        self.errorClose.pack(side="right")

        self.historyPadding = tkinter.Frame(self.history_frame)
       

        self.datesList = tkinter.Listbox(self.sidebar)
        self.datesList.pack(fill="both", expand=True)
        self.datesList.insert(0, "Today")
        self.datesList.insert(1, "Yesterday")
        self.datesList.insert(2, "Last week")
        self.datesList.insert(3, "30 days ago")
        self.datesList.insert(4, "All time")
        self.datesList.bind("<<ListboxSelect>>", self.jumpToDate)

        self.clear_button = ttk.Button(self.sidebar, text="Clear History", command=self.clear_history)
        self.clear_button.pack(side="bottom", fill="x")

        self.history_container = tkinter.Canvas(self.history_frame)
        self.history_container.pack(side="right", fill="both", expand=True)
        self.history_list = ttk.Frame(self.history_container)
        self.history_list_window = self.history_container.create_window((0,0), window=self.history_list, anchor="nw")
        self.history_seperators = []
        self.history_items = []

        self.history_scrollbar = ttk.Scrollbar(self.history_container, orient="vertical", command=self.history_container.yview)
        self.history_scrollbar.pack(side="right", fill="y")

        self.history_list.bind("<Configure>", self._center_history_list)
        self.history_container.configure(yscrollcommand=self.handle_scroll)

        self.history_container.bind("<MouseWheel>", lambda e: self.history_container.yview_scroll(int(-1*(e.delta/120)), "units"))
                
        self.historyURL = None
        self.isEnabled = False
        self.previousDate = None
        self.searching = False
        # Chunk limits
        self.currentlyLoadedItems = 0
        self.targetLoadedItems = 16
        #Advanced Search
        self.advancedSearchCriteria = ["URL","Title","Date range","Before date","After date"]


    def clear_history(self):
        self.clearDialog = tkinter.Toplevel()
        self.clearDialog.title("Clear History")
        self.clearDialog.geometry("300x100")
        self.clearDialog.resizable(False, False)

        self.clearText = tkinter.Label(self.clearDialog, text="Delete all history from:")
        self.clearText.pack(side="top")

        self.times = ["Last hour", "Last 24 hours", "Last 7 days", "Last 4 weeks", "All time", "Custom"]
        self.timeDropdown = ttk.Combobox(self.clearDialog, state='readonly', values=self.times)
        self.timeDropdown.current(4)
        self.timeDropdown.pack(side="top")

        self.buttonFrame = ttk.Frame(self.clearDialog,style="Card.TFrame")
        self.buttonFrame.pack(side="bottom", fill="x")

        self.clearButton = ttk.Button(self.buttonFrame, text="Clear", style="Accent.TButton", command=fileHandler.clearHistory)
        self.clearButton.pack(side="right")
        self.cancelButton = ttk.Button(self.buttonFrame, text="Cancel", command=self.clearDialog.destroy)
        self.cancelButton.pack(side="right")

    def handle_scroll(self, y0, y1):
        self.history_scrollbar.set(y0,y1) # Set scrollbar length
        if float(y1)>0.9 and self.isEnabled: # Load in next chunk of history
            newTargetLoadedItems = self.targetLoadedItems+16
            if newTargetLoadedItems>len(fileHandler.historyTimeAccessed):
                self.targetLoadedItems = len(fileHandler.historyTimeAccessed)
            else:
                self.targetLoadedItems = newTargetLoadedItems
            self.load_history(supressEventGeneration=True) # Load next chunk of history, but do not report it to tabFrame
    
    def load_history(self,supressEventGeneration = False):
        if len(fileHandler.historyURL) == 0 or self.searching:
            print("[History] No history")
            self.no_history_image = tkinter.PhotoImage(file=fileHandler.noShortcut)
            self.nohistorytext = tkinter.Label(self.history_list, text="No history found", font=("TkDefaultFont", 16), image=self.no_history_image, compound="top")
            self.nohistorytext.pack()
        elif self.searching: #Will only load search results
            self.progress.pack(side="top", fill="x")
            progress_steps = 100 / len(fileHandler.historyURL)
            ##self.history_seperators.clear()
            ##self.history_items.clear()
            reversedTimes = list(reversed(fileHandler.historyTimeAccessed))
            for i in range(self.targetLoadedItems-self.currentlyLoadedItems):
                item = reversedTimes[int(i)+self.currentlyLoadedItems]
                print(f"[History] Processing item {item}")
                itemNumber = fileHandler.historyTimeAccessed.index(item)
                itemDate = datetime.datetime.strptime(item,"%Y-%m-%d %H:%M:%S")
                self.progress.step(progress_steps)

                # Generate item frame
                self.history_items.append(ttk.Frame(self.history_list,cursor="hand2"))
                self.history_items[-1].iconImage = tkinter.PhotoImage(file=fileHandler.historyIcons[itemNumber] if os.path.exists(fileHandler.historyIcons[itemNumber]) else fileHandler.noIcon)
                self.history_items[-1].iconLabel = ttk.Label(self.history_items[-1], text=fileHandler.historyTitles[itemNumber],image=self.history_items[-1].iconImage, style="TButton", compound="left")
                self.history_items[-1].iconLabel.pack(side="top", fill = "x")
                self.history_items[-1].bottomFrame = ttk.Frame(self.history_items[-1])
                self.history_items[-1].bottomFrame.pack(side="top",fill="x")
                self.history_items[-1].timeLabel = tkinter.Label(self.history_items[-1].bottomFrame,text=f"{itemDate.time()}", font=("TkDefaultFont",10))
                self.history_items[-1].timeLabel.pack(side = "left")
                self.history_items[-1].seperator = ttk.Separator(self.history_items[-1].bottomFrame, orient="vertical")
                self.history_items[-1].seperator.pack(side="left")
                self.history_items[-1].urlLabel = tkinter.Label(self.history_items[-1].bottomFrame,text=f"{fileHandler.historyURL[itemNumber]}", font=("TkDefaultFont",10,"italic"))
                self.history_items[-1].urlLabel.pack(side = "left")
                self.history_items[-1].itemNumber = itemNumber
                self.history_items[-1].bind("<Button-1>", lambda e, url=fileHandler.historyURL[self.history_items[-1].itemNumber]: self.setUrl(url))
                self.history_items[-1].iconLabel.bind("<Button-1>",lambda e, url=fileHandler.historyURL[self.history_items[-1].itemNumber]: self.setUrl(url))
                self.history_items[-1].bottomFrame.bind("<Button-1>", lambda e, url=fileHandler.historyURL[self.history_items[-1].itemNumber]: self.setUrl(url))

                #Detect changes in date and generate seperators
                if self.previousDate != itemDate.date():
                    self.history_seperators.append(tkinter.Label(self.history_list, text=humanize.naturalday(itemDate.date()).capitalize(), font=("TkDefaultFont", 14)))
                    self.history_seperators[-1].pack(side = "top")
                    print(f"[History] New date detected, adding seperator for {itemDate.date()}")
                    
                self.history_items[-1].pack(side = "top", anchor="w", fill="x")
                self.previousDate=itemDate.date()
            self.progress.pack_forget()
            self.history_scrollbar.update()
            if not supressEventGeneration:
                self.history_list.event_generate("<<DoneLoading>>")
            self.currentlyLoadedItems=self.targetLoadedItems
        else:
            self.progress.pack(side="top", fill="x")
            progress_steps = 100 / len(fileHandler.historyURL)
            ##self.history_seperators.clear()
            ##self.history_items.clear()
            reversedTimes = list(reversed(fileHandler.historyTimeAccessed))
            for i in range(self.targetLoadedItems-self.currentlyLoadedItems):
                item = reversedTimes[int(i)+self.currentlyLoadedItems]
                print(f"[History] Processing item {item}")
                itemNumber = fileHandler.historyTimeAccessed.index(item)
                itemDate = datetime.datetime.strptime(item,"%Y-%m-%d %H:%M:%S")
                self.progress.step(progress_steps)

                # Generate item frame
                self.history_items.append(ttk.Frame(self.history_list,cursor="hand2"))
                self.history_items[-1].iconImage = tkinter.PhotoImage(file=fileHandler.historyIcons[itemNumber] if os.path.exists(fileHandler.historyIcons[itemNumber]) else fileHandler.noIcon)
                self.history_items[-1].iconLabel = ttk.Label(self.history_items[-1], text=fileHandler.historyTitles[itemNumber],image=self.history_items[-1].iconImage, style="TButton", compound="left")
                self.history_items[-1].iconLabel.pack(side="top", fill = "x")
                self.history_items[-1].bottomFrame = ttk.Frame(self.history_items[-1])
                self.history_items[-1].bottomFrame.pack(side="top",fill="x")
                self.history_items[-1].timeLabel = tkinter.Label(self.history_items[-1].bottomFrame,text=f"{itemDate.time()}", font=("TkDefaultFont",10))
                self.history_items[-1].timeLabel.pack(side = "left")
                self.history_items[-1].seperator = ttk.Separator(self.history_items[-1].bottomFrame, orient="vertical")
                self.history_items[-1].seperator.pack(side="left")
                self.history_items[-1].urlLabel = tkinter.Label(self.history_items[-1].bottomFrame,text=f"{fileHandler.historyURL[itemNumber]}", font=("TkDefaultFont",10,"italic"))
                self.history_items[-1].urlLabel.pack(side = "left")
                self.history_items[-1].itemNumber = itemNumber
                self.history_items[-1].bind("<Button-1>", lambda e, url=fileHandler.historyURL[self.history_items[-1].itemNumber]: self.setUrl(url))
                self.history_items[-1].iconLabel.bind("<Button-1>",lambda e, url=fileHandler.historyURL[self.history_items[-1].itemNumber]: self.setUrl(url))
                self.history_items[-1].bottomFrame.bind("<Button-1>", lambda e, url=fileHandler.historyURL[self.history_items[-1].itemNumber]: self.setUrl(url))

                #Detect changes in date and generate seperators
                if self.previousDate != itemDate.date():
                    self.history_seperators.append(tkinter.Label(self.history_list, text=humanize.naturalday(itemDate.date()).capitalize(), font=("TkDefaultFont", 14)))
                    self.history_seperators[-1].pack(side = "top")
                    print(f"[History] New date detected, adding seperator for {itemDate.date()}")
                    
                self.history_items[-1].pack(side = "top", anchor="w", fill="x")
                self.previousDate=itemDate.date()
            self.progress.pack_forget()
            self.history_scrollbar.update()
            if not supressEventGeneration:
                self.history_list.event_generate("<<DoneLoading>>")
            self.currentlyLoadedItems=self.targetLoadedItems

    def setUrl(self, url):
        self.history_list.event_generate("<<HistoryURLClicked>>")    
        self.historyURL = url
        print(f"[History] URL set to {self.historyURL}")

    def _center_history_list(self, event):
        canvas_width = event.width
        frame_width = self.history_list.winfo_reqwidth()
        # Responsive horizontal padding: 10% of canvas width, minimum 20px
        pad_x = max(int(canvas_width * 0.1), 20)
        # Center the frame horizontally
        x = (canvas_width - frame_width) // 2 if canvas_width > frame_width else 0
        self.history_container.coords(self.history_list_window, x, 0)
        self.history_list.configure(padding=(pad_x, 10, pad_x, 10))  # (left, top, right, bottom)
        self.history_container.configure(scrollregion=self.history_container.bbox("all"))
    
    def jumpToDate(self,event = None):
        selected_date = self.datesList.get(self.datesList.curselection())
        print(f"[History] Jumping to date: {selected_date}")
        setPoint = 0
        if selected_date == "Today":
            setPoint = 0
        elif selected_date == "Yesterday":
            setDate = datetime.datetime.now() - datetime.timedelta(days=1)
            for i, timeStr in enumerate(reversed(fileHandler.historyTimeAccessed)):
                itemDate = datetime.datetime.strptime(timeStr,"%Y-%m-%d %H:%M:%S").date()
                if itemDate < setDate.date():
                    setPoint = i / len(fileHandler.historyTimeAccessed)
                    self.currentlyLoadedItems = i+16
                    break
            else:
                setPoint = 0
                self.showError("No websites were visited yesterday")
        elif selected_date == "Last week":
            setDate = datetime.datetime.now() - datetime.timedelta(days=7)
            for i, timeStr in enumerate(reversed(fileHandler.historyTimeAccessed)):
                itemDate = datetime.datetime.strptime(timeStr,"%Y-%m-%d %H:%M:%S").date()
                if itemDate < setDate.date():
                    setPoint = i / len(fileHandler.historyTimeAccessed)
                    self.currentlyLoadedItems = i+16
                    break
            else:
                setPoint = 0
                self.showError("No websites were visited last week")
        elif selected_date == "30 days ago":
            setDate = datetime.datetime.now() - datetime.timedelta(days=30)
            for i, timeStr in enumerate(reversed(fileHandler.historyTimeAccessed)):
                itemDate = datetime.datetime.strptime(timeStr,"%Y-%m-%d %H:%M:%S").date()
                if itemDate < setDate.date():
                    setPoint = i / len(fileHandler.historyTimeAccessed)
                    self.currentlyLoadedItems = i+16
                    break
            else:
                setPoint = 0
                self.showError("No websites were visited 30 days ago")
        elif selected_date == "All time":
            setPoint = 0
        self.load_history()
        self.history_container.yview_moveto(setPoint)    
        
    def showError(self,text):
            self.errorText.config(text=text)
            self.errorBar.pack(side="top",fill = "x")
    
    #Search commands
    def searchOptions(self):
        self.searchDialog = tkinter.Toplevel()
        self.searchDialog.title("Search Options")
        self.searchDialog.geometry("500x200")

        self.advancedFrame = ttk.LabelFrame(self.searchDialog,text="Advanced Search")
        self.advancedFrame.pack(side="top",fill="both")
        self.fieldsFrame = ttk.Frame(self.advancedFrame)
        self.fieldsFrame.pack(expand=True,fill="both")
        self.fields = []
        self.fields.append(tkinter.Frame(self.fieldsFrame))
        self.fields[0].pack(side = "top",fill = "x")
        self.fields[0].criteriaSelector = ttk.Combobox(self.fields[0],state="readonly",values=self.advancedSearchCriteria)
        self.fields[0].criteriaSelector.pack(side="left",expand=False)
        self.fields[0].criteriaSelector.bind("<<ComboboxSelected>>",lambda e:self.itemSelected(self.fields[0]))
        self.addButton = ttk.Button(self.advancedFrame,text = "+ Add Criteria", state= "disabled",command = self.addCriteria) #Disabled until criteria checked
        self.addButton.pack(side="bottom",anchor="sw")
        
        self.searchFrame = ttk.Frame(self.searchDialog,style="Card.TFrame")
        self.searchFrame.pack(side="bottom", fill="x")
        self.searchButton = ttk.Button(self.searchFrame, text="Search", style="Accent.TButton", command=self.acceptSearchOptions)
        self.searchButton.pack(side="right")
        self.cancelButton = ttk.Button(self.searchFrame, text="Cancel", command=self.searchDialog.destroy)
        self.cancelButton.pack(side="right")
    
    def itemSelected(self,itemFrame):
        self.addButton.config(state="normal")
        itemSelection = itemFrame.criteriaSelector.get()
        # Destroy previous widgets in the frame
        try:
            itemFrame.textContainer.destroy()
        except:
            pass
        try:
            itemFrame.urlText.destroy()
        except:
            pass
        try:
            itemFrame.titleText.destroy()
        except:
            pass
        try:
            itemFrame.afterDate.destroy()
        except:
            pass
        try:
            itemFrame.beforeDate.destroy()
            itemFrame.dash.destroy()
        except:
            pass
        itemFrame.textContainer = tkinter.Frame(itemFrame)
        itemFrame.textContainer.pack(side="left", fill="x")
        if itemSelection == "URL":
            itemFrame.urlText = ttk.Entry(itemFrame.textContainer)
            itemFrame.urlText.pack(fill = "x")
        if itemSelection == "Title":
            itemFrame.titleText = ttk.Entry(itemFrame.textContainer)
            itemFrame.titleText.pack(fill="x")
        if itemSelection == "Date range":
            itemFrame.afterDate = tkcalendar.DateEntry(itemFrame.textContainer)
            itemFrame.afterDate.pack(side = "left",fill = "x")
            itemFrame.dash = tkinter.Label(itemFrame.textContainer,text="-")
            itemFrame.dash.pack(side="left")
            itemFrame.beforeDate = tkcalendar.DateEntry(itemFrame.textContainer)
            itemFrame.beforeDate.pack(side = "left",fill = "x")
        if itemSelection == "Before date":
            itemFrame.beforeDate = tkcalendar.DateEntry(itemFrame.textContainer)
            itemFrame.beforeDate.pack(side = "left",fill = "x")
        if itemSelection == "After date":
            itemFrame.afterDate = tkcalendar.DateEntry(itemFrame.textContainer)
            itemFrame.afterDate.pack(side = "left",fill = "x")

    def addCriteria(self):
        self.fields.append(tkinter.Frame(self.fieldsFrame))
        self.fields[-1].pack(side = "top",fill = "x")
        fieldIndex = self.fields.index(self.fields[-1])
        self.fields[-1].removeButton = ttk.Button(self.fields[-1],text="-",command=lambda: self.removeCriteria(self.fields[fieldIndex]))
        self.fields[-1].removeButton.pack(side="left")
        self.fields[-1].criteriaSelector = ttk.Combobox(self.fields[-1],state="readonly",values=self.advancedSearchCriteria)
        self.fields[-1].criteriaSelector.pack(side="left",expand=False)
        self.fields[-1].criteriaSelector.bind("<<ComboboxSelected>>",lambda e:self.itemSelected(self.fields[fieldIndex]))
        self.searchDialog.geometry(f"{str(self.searchDialog.winfo_width())}x{str(self.searchDialog.winfo_height()+32)}")
        self.addButton.configure(state="disabled")

    def removeCriteria(self,item):
        itemIndex = self.fields.index(item)
        item.destroy()
        self.searchDialog.geometry(f"{str(self.searchDialog.winfo_width())}x{str(self.searchDialog.winfo_height()-32)}")
        try:
            if self.fields[itemIndex-1].criteriaSelector.get() is None or self.fields[itemIndex+1].criteriaSelector.get() is None:
                self.addButton.configure(state="disabled")
        except IndexError:
            pass
    
    def acceptSearchOptions(self):
        currentText = self.search_bar.get()
        if currentText == self.defaultText.get():
            currentText = ""
            self.enterSearch()
        for item in self.fields:
            try:
                itemType = item.criteriaSelector.get()
                if itemType == "URL":
                    currentText = currentText + " url:'" + item.urlText.get()+"'"
                elif itemType == "Title":
                    currentText = currentText + " title:'" + item.titleText.get()+"'"
                elif itemType == "Date range":
                    currentText = currentText + " date:" + str(item.afterDate.get_date())+","+str(item.beforeDate.get_date())
                elif itemType == "Before date":
                    currentText = currentText + " before:" + str(item.beforeDate.get_date())
                elif itemType == "After date":
                    currentText = currentText + " after:" + str(item.afterDate.get_date())
            except Exception as e:
                print(f"[HISTORY] Criteria could not be loaded because: {e}")
        self.searchText.set(currentText)
        self.searchDialog.destroy()
    
    def enterSearch(self,event=None):
        if not self.searching:
            self.search_bar.configure(textvariable=self.searchText)
            self.advancedButton.pack_forget()
            self.deleteButton.pack(side = "left")
            self.advancedButton.pack(side="left")
            self.searching = True
    
    def cancelSearch(self,event=None):
        self.searchText.set("")
        self.deleteButton.pack_forget()
        self.search_bar.configure(textvariable=self.defaultText)
        self.searching=False

    def search(self, *args):
        query = self.searchText.get() #Original query
        filters = []
        word = "" #A single word from the query to find search criteria
        isAFilter = False
        refinedQuery = "" #Version of the query without advanced search criteria
        wordCount = 0
        for char in query:
            if char == " " and not word == "" and not isAFilter:
                refinedQuery=refinedQuery+word
                word = ""
                wordCount += 1
            if char == " " and not word == "" and isAFilter:
                filters[-1].text = word
                word = ""
            if char == " " and word == "" and isAFilter:
                filters.pop(-1)
            if char == " " and word == "" and not isAFilter:
                refinedQuery = refinedQuery 
            if char == ":":
                filters.append(word)
                word = ""
            else:
                word=word+char        
        if wordCount == 0:#Add incomplete words
            refinedQuery = word
        else:
            refinedQuery = refinedQuery+word 
        print(f"[History] Searching for query {refinedQuery}")