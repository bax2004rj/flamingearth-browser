import tkinter
from tkinter import ttk,messagebox
import fileHandler
import sv_ttk
import os
import datetime

class Bookmarks:
    def __init__(self,tab):
        self.bookmarks_frame = ttk.Frame(tab)

        self.topbar = ttk.Frame(self.bookmarks_frame, style = "Card.TFrame")
        self.topbar.pack(side="top", fill="x")

        self.sidebar = tkinter.Frame(self.bookmarks_frame)
        self.sidebar.pack(side="left", fill="y")

        self.progress = ttk.Progressbar(self.topbar)

        self.top_label = ttk.Label(self.topbar, text="Bookmarks",font=("TkDefaultFont", 16))
        self.top_label.pack(side="left", padx=10)

        self.folderButton = ttk.Button(self.topbar,text="New Folder")
        self.folderButton.pack(side = "left")
        self.bookmarkButton = ttk.Button(self.topbar,text="New Bookmark")
        self.bookmarkButton.pack(side = "left")

        self.searchFrame = ttk.Frame(self.topbar)
        self.searchFrame.pack()

        self.defaultText = tkinter.StringVar(self.searchFrame,value="Search through bookmarks… (↵ to search)")
        self.searchText = tkinter.StringVar(self.searchFrame)
        self.search_bar = ttk.Entry(self.searchFrame,textvariable=self.defaultText)
        self.search_bar.pack(side = "left", expand= 1)
        self.search_bar.bind("<FocusIn>",self.enterSearch)
        self.search_bar.bind("<Return>",self.search)
        ##self.searchText.trace_add("write",self.search) ## Instantly tracking search caused issues with rendering, so it searches on enter press
        self.deleteButton = ttk.Button(self.searchFrame,text="⌫", style= "Accent.TButton",command=self.cancelSearch)

        self.errorBar = ttk.Frame(self.topbar, style = "TEntry")
        self.errorText = ttk.Label(self.errorBar,text="")
        self.errorText.pack(in_=self.errorBar, side="left", padx=10, fill = "x")
        self.errorClose = ttk.Button(self.errorBar, text="OK", style = "Accent.TButton", command=self.errorBar.pack_forget)
        self.errorClose.pack(side="right")

        self.bookmarksPadding = tkinter.Frame(self.bookmarks_frame)
       

        self.foldersList = tkinter.Listbox(self.sidebar)
        self.foldersList.bind("<<ListboxSelect>>", self.jumpToSubfolder)

        self.bookmarks_container = tkinter.Canvas(self.bookmarks_frame)
        self.bookmarks_container.pack(side="right", fill="both", expand=True)
        self.bookmarks_list = ttk.Frame(self.bookmarks_container)
        self.bookmarks_list_window = self.bookmarks_container.create_window((0,0), window=self.bookmarks_list, anchor="nw")
        self.bookmarks_seperators = []
        self.bookmarks_items = []

        self.bookmarks_scrollbar = ttk.Scrollbar(self.bookmarks_container, orient="vertical", command=self.bookmarks_container.yview)
        self.bookmarks_scrollbar.pack(side="right", fill="y")

        self.bookmarks_list.bind("<Configure>", self._center_bookmarks_list)
        self.bookmarks_container.configure(yscrollcommand=self.handle_scroll)

        self.bookmarks_container.bind("<MouseWheel>", lambda e: self.bookmarks_container.yview_scroll(int(-1*(e.delta/120)), "units"))
                
        self.bookmarksURL = None
        self.isEnabled = False
        self.previousDate = None
        self.searching = False
        self.searchRenderRunning = False
        # Chunk limits
        self.currentlyLoadedItems = 0
        self.targetLoadedItems = 16
        # Search
        self.foundIndicies = []

    def handle_scroll(self, y0, y1):
        self.bookmarks_scrollbar.set(y0,y1) # Set scrollbar length
        if float(y1)>0.9 and self.isEnabled and self.searchRenderRunning == False: # Load in next chunk of bookmarks
            newTargetLoadedItems = self.targetLoadedItems+16
            if newTargetLoadedItems>len(fileHandler.bookmarks):
                self.targetLoadedItems = len(fileHandler.bookmarks)
            else:
                self.targetLoadedItems = newTargetLoadedItems
            self.load_bookmarks(supressEventGeneration=True) # Load next chunk of bookmarks, but do not report it to tabFrame
    
    def load_bookmarks(self,supressEventGeneration = False):
        if len(fileHandler.bookmarks) == 0 and not self.searching:
            print("[Bookmarks] No bookmarks")
            self.no_bookmarks_image = tkinter.PhotoImage(file=fileHandler.noShortcut)
            self.nobookmarkstext = tkinter.Label(self.bookmarks_list, text="No bookmarks found", font=("TkDefaultFont", 16), image=self.no_bookmarks_image, compound="top")
            self.nobookmarkstext.pack()
        elif len(self.foundIndicies) == 0 and self.searching:
            self.destroyAllItems()
            print("[Bookmarks] No bookmarks")
            self.no_bookmarks_image = tkinter.PhotoImage(file=fileHandler.noShortcut)
            self.nobookmarkstext = tkinter.Label(self.bookmarks_list, text="No results found", font=("TkDefaultFont", 16), image=self.no_bookmarks_image, compound="top")
            self.nobookmarkstext.pack()
        elif self.searching: #Will only load search results
            self.searchRenderRunning = True
            self.progress.pack(side="top", fill="x")
            progress_steps = 100 / len(fileHandler.bookmarks)
            ##self.bookmarks_seperators.clear()
            ##self.bookmarks_items.clear()
            reversedTimes = list(reversed(fileHandler.bookmarks))
            for i in range(self.targetLoadedItems-self.currentlyLoadedItems):
                try:
                    itemIndex = self.foundIndicies[int(i)+self.currentlyLoadedItems]
                except IndexError:
                    print("[Bookmarks] Cannot continue loading chunk, all items already listed")
                    break
                item = reversedTimes[itemIndex]
                print(f"[Bookmarks] Processing item {item}")
                itemNumber = fileHandler.bookmarks.index(item)
                self.progress.step(progress_steps)

                # Generate item frame
                self.bookmarks_items.append(ttk.Frame(self.bookmarks_list,cursor="hand2"))
                self.bookmarks_items[-1].iconImage = tkinter.PhotoImage(file=fileHandler.bookmarks[itemNumber]["icon"] if os.path.exists(fileHandler.bookmarksIcons[itemNumber]) else fileHandler.noIcon)
                self.bookmarks_items[-1].iconLabel = ttk.Label(self.bookmarks_items[-1], text=fileHandler.bookmarks[itemNumber]["title"],image=self.bookmarks_items[-1].iconImage, style="TButton", compound="left")
                self.bookmarks_items[-1].iconLabel.pack(side="top", fill = "x")
                self.bookmarks_items[-1].bottomFrame = ttk.Frame(self.bookmarks_items[-1])
                self.bookmarks_items[-1].bottomFrame.pack(side="top",fill="x")
                self.bookmarks_items[-1].urlLabel = tkinter.Label(self.bookmarks_items[-1].bottomFrame,text=f"{fileHandler.bookmarks[itemNumber]["url"]}", font=("TkDefaultFont",10,"italic"))
                self.bookmarks_items[-1].urlLabel.pack(side = "left")
                self.bookmarks_items[-1].itemNumber = itemNumber
                self.bookmarks_items[-1].bind("<Button-1>", lambda e, url=fileHandler.bookmarks[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
                self.bookmarks_items[-1].iconLabel.bind("<Button-1>",lambda e, url=fileHandler.bookmarks[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
                self.bookmarks_items[-1].bottomFrame.bind("<Button-1>", lambda e, url=fileHandler.bookmarks[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
            
                self.bookmarks_items[-1].pack(side = "top", anchor="w", fill="x")
            self.progress.pack_forget()
            self.bookmarks_scrollbar.update()
            if not supressEventGeneration:
                self.bookmarks_list.event_generate("<<DoneLoading>>")
            self.currentlyLoadedItems=self.targetLoadedItems
            self.searchRenderRunning=False 
        else:
            self.progress.pack(side="top", fill="x")
            progress_steps = 100 / len(fileHandler.bookmarks)
            ##self.bookmarks_seperators.clear()
            ##self.bookmarks_items.clear()
            for i in range(self.targetLoadedItems-self.currentlyLoadedItems):
                item = fileHandler.bookmarks[int(i)+self.currentlyLoadedItems]
                print(f"[Bookmarks] Processing item {item}")
                itemNumber = fileHandler.bookmarks.index(item)
                itemDate = datetime.datetime.strptime(item,"%Y-%m-%d %H:%M:%S")
                self.progress.step(progress_steps)

                # Generate item frame
                self.bookmarks_items.append(ttk.Frame(self.bookmarks_list,cursor="hand2"))
                self.bookmarks_items[-1].iconImage = tkinter.PhotoImage(file=fileHandler.bookmarks[itemNumber]["icon"] if os.path.exists(fileHandler.bookmarksIcons[itemNumber]) else fileHandler.noIcon)
                self.bookmarks_items[-1].iconLabel = ttk.Label(self.bookmarks_items[-1], text=fileHandler.bookmarks[itemNumber]["title"],image=self.bookmarks_items[-1].iconImage, style="TButton", compound="left")
                self.bookmarks_items[-1].iconLabel.pack(side="top", fill = "x")
                self.bookmarks_items[-1].bottomFrame = ttk.Frame(self.bookmarks_items[-1])
                self.bookmarks_items[-1].bottomFrame.pack(side="top",fill="x")
                self.bookmarks_items[-1].urlLabel = tkinter.Label(self.bookmarks_items[-1].bottomFrame,text=f"{fileHandler.bookmarks[itemNumber]["url"]}", font=("TkDefaultFont",10,"italic"))
                self.bookmarks_items[-1].urlLabel.pack(side = "left")
                self.bookmarks_items[-1].itemNumber = itemNumber
                self.bookmarks_items[-1].bind("<Button-1>", lambda e, url=fileHandler.bookmarks[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
                self.bookmarks_items[-1].iconLabel.bind("<Button-1>",lambda e, url=fileHandler.bookmarks[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
                self.bookmarks_items[-1].bottomFrame.bind("<Button-1>", lambda e, url=fileHandler.bookmarks[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
            
                self.bookmarks_items[-1].pack(side = "top", anchor="w", fill="x")
                self.previousDate=itemDate.date()
            self.progress.pack_forget()
            self.bookmarks_scrollbar.update()
            if not supressEventGeneration:
                self.bookmarks_list.event_generate("<<DoneLoading>>")
            self.currentlyLoadedItems=self.targetLoadedItems

    def destroyAllItems(self):
        for i in self.bookmarks_items:
            i.destroy()
        for i in self.bookmarks_seperators:
            i.destroy()
        self.bookmarks_items.clear()
        self.bookmarks_seperators.clear()
        try:
            self.nobookmarkstext.destroy()
        except Exception:
            pass
        self.bookmarks_list.update_idletasks()
        self.bookmarks_container.configure(scrollregion=self.bookmarks_container.bbox("all"))

    def setUrl(self, url):
        self.bookmarks_list.event_generate("<<BookmarksURLClicked>>")    
        self.bookmarksURL = url
        print(f"[Bookmarks] URL set to {self.bookmarksURL}")

    def _center_bookmarks_list(self, event):
        canvas_width = event.width
        frame_width = self.bookmarks_list.winfo_reqwidth()
        # Responsive horizontal padding: 10% of canvas width, minimum 20px
        pad_x = max(int(canvas_width * 0.1), 20)
        # Center the frame horizontally
        x = (canvas_width - frame_width) // 2 if canvas_width > frame_width else 0
        self.bookmarks_container.coords(self.bookmarks_list_window, x, 0)
        self.bookmarks_list.configure(padding=(pad_x, 10, pad_x, 10))  # (left, top, right, bottom)
        self.bookmarks_container.configure(scrollregion=self.bookmarks_container.bbox("all"))
    
    def jumpToSubfolder(self,event = None):
        selected_date = self.foldersList.get(self.foldersList.curselection())
        print(f"[Bookmarks] Jumping to date: {selected_date}")
    
    def enterSearch(self,event=None):
        if not self.searching:
            self.search_bar.configure(textvariable=self.searchText)
            self.deleteButton.pack(side = "left")
            self.searching = True
    
    def cancelSearch(self,event=None):
        self.searchText.set("")
        self.deleteButton.pack_forget()
        self.search_bar.configure(textvariable=self.defaultText)
        self.destroyAllItems()
        self.searching=False
        self.load_bookmarks(supressEventGeneration=True)

    def search(self, *args):
        query = self.searchText.get() #Original query
        filters = []
        filterParameters = []
        self.foundIndicies=[] #Wipe previous results
        word = "" #A single word from the query to find search criteria
        isAFilter = False
        existingQuotationMark = False
        refinedQuery = "" #Version of the query without advanced search criteria
        wordCount = 0
        for char in query:
            if char == " " and not word == "" and not isAFilter:
                refinedQuery=refinedQuery+word+" "
                word = ""
                wordCount += 1
            elif char == "\"" and not word == "" and isAFilter and existingQuotationMark:
                filterParameters.append(word)
                word = ""
                isAFilter = False
                existingQuotationMark = False
            elif char == "\"" and isAFilter and not existingQuotationMark:
                word=word+char
                existingQuotationMark=True
            elif char == "\"" and word == "" and isAFilter and existingQuotationMark:
                filters.pop(-1)
                isAFilter = False
            elif char == " " and word == "" and not isAFilter:
                pass
            elif char == ":":
                filters.append(word)
                word = ""
                isAFilter = True
            else:
                word=word+char        
        if wordCount == 0:#Add incomplete words
            refinedQuery = word
        else:
            refinedQuery = refinedQuery+word 
        print(f"[History] Searching for query \"{refinedQuery}\". {len(filters)} filter(s) found, with {len(filterParameters)} parameter(s) found")
        # Eliminate everything not applied to filters
        filteredIndices = []
        if not refinedQuery == "":
            for i in filteredIndices:
                if word in fileHandler.bookmarks[i]["title"] or word in fileHandler.bookmarks[i]["url"]:
                    self.foundIndicies.append(i)
        else:
            self.foundIndicies = filteredIndices
        print(f"[History] {len(self.foundIndicies)} items found")
        self.currentlyLoadedItems = 0
        self.targetLoadedItems = 16
        if not self.searchRenderRunning:
            self.destroyAllItems()
            self.load_bookmarks(supressEventGeneration=True)
        else:
            print("Search still rendering")