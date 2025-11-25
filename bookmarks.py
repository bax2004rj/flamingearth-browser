import tkinter
from tkinter import ttk,messagebox
import fileHandler
import sv_ttk
import os
import datetime
import json

class Bookmarks:
    def __init__(self,tab):
        self.bookmarks_frame = ttk.Frame(tab)

        self.topbar = ttk.Frame(self.bookmarks_frame, style = "Card.TFrame")
        self.topbar.pack(side="top", fill="x")

        self.sidebar = ttk.Treeview(self.bookmarks_frame)
        self.sidebar.pack(side="left", fill="y")

        self.progress = ttk.Progressbar(self.topbar)

        self.top_label = ttk.Label(self.topbar, text="Bookmarks",font=("TkDefaultFont", 16))
        self.top_label.pack(side="left", padx=10)

        self.folderButton = ttk.Button(self.topbar,text="New Folder",command=self.addFolder)
        self.folderButton.pack(side = "left")
        self.bookmarkButton = ttk.Button(self.topbar,text="New Bookmark",command=self.addBookmark)
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
       

        self.foldersList = ttk.Treeview(self.sidebar)
        self.foldersList.bind("<<TreeviewSelect>>", self.jumpToSubfolder)
        self.foldersList["columns"]=["folders"]
        self.foldersList.column("#0",width=16,stretch=tkinter.NO)
        self.foldersList.column("folders",width=200)
        self.foldersList.heading("folders",text="Folders")
        self.foldersList.pack(side="top",fill="both",expand=1)
        self.foldersDropdownOptions = ["/"]

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
                
        self.bookmarksURL = "flamingearth://bookmarks"
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
    
    def checkDirExistenceAndReturn(self, url):
        bookmarksList = fileHandler.bookmarks
        if url.startswith("flamingearth://bookmarks"):
            bookmarksFolder = url.split("/")[3:]
            print(f"[Bookmarks] Attempting to navigate to folder {bookmarksFolder}")
            for i in bookmarksFolder: # Test subfolder existence
                itemExists = False
                # Ensure we are iterating a list of items
                if not isinstance(bookmarksList, list):
                    bookmarksList = []
                    break
                for j in bookmarksList:
                    print(j)
                    if i == j.get("title"):
                        print(f"[Bookmarks] Subfolder {i} exists!")
                        # j is a folder dict; get its "items" list (or empty list if none)
                        bookmarksList = j.get("items", [])
                        itemExists = True
                        break
                if not itemExists:
                    print(f"[Bookmarks] Subfolder {i} does not exist!")
                    bookmarksList = [] # Set list to nothing to show no bookmarks message.
                    break
        return bookmarksList

    def load_bookmarks(self,supressEventGeneration = False):
        bookmarksList = self.checkDirExistenceAndReturn(self.bookmarksURL)
        if len(bookmarksList) == 0 and not self.searching:
            print("[Bookmarks] No bookmarks")
            self.no_bookmarks_image = tkinter.PhotoImage(file=fileHandler.noShortcut)
            try:
                self.nobookmarkstext.pack_forget()
            except Exception:
                print("[Bookmarks] No bookmarks, did not remove previous text (it most likely didn't exist before this)")
            self.nobookmarkstext = tkinter.Label(self.bookmarks_list, text="No bookmarks found", font=("TkDefaultFont", 16), image=self.no_bookmarks_image, compound="top")
            self.nobookmarkstext.pack()
        elif len(self.foundIndicies) == 0 and self.searching:
            self.destroyAllItems()
            print("[Bookmarks] No bookmarks")
            self.no_bookmarks_image = tkinter.PhotoImage(file=fileHandler.noShortcut)
            try:
                self.nobookmarkstext.pack_forget()
            except Exception:
                print("[Bookmarks] No bookmarks, did not remove previous text (it most likely didn't exist before this)")
            self.nobookmarkstext = tkinter.Label(self.bookmarks_list, text="No results found", font=("TkDefaultFont", 16), image=self.no_bookmarks_image, compound="top")
            self.nobookmarkstext.pack()
        else:
            if self.searching:
                self.searchRenderRunning = True
            self.progress.pack(side="top", fill="x")
            progress_steps = 100 / len(bookmarksList)
            ##self.bookmarks_seperators.clear()
            ##self.bookmarks_items.clear()
            try:
                for i in range(self.targetLoadedItems-self.currentlyLoadedItems):
                    item = bookmarksList[int(i)+self.currentlyLoadedItems]
                    print(f"[Bookmarks] Processing item {item}")
                    itemNumber = bookmarksList.index(item)
                    self.progress.step(progress_steps)

                    # Generate item frame
                    self.bookmarks_items.append(ttk.Frame(self.bookmarks_list,cursor="hand2"))
                    if bookmarksList[itemNumber]["type"]=="folder":
                        self.bookmarks_items[-1].iconLabel = ttk.Label(self.bookmarks_items[-1], text=bookmarksList[itemNumber]["title"], style="TButton", compound="left") ##TODO: add image=self.bookmarks_items[-1].iconImage, back
                        self.bookmarks_items[-1].iconLabel.pack(side="top", fill = "x")
                        self.bookmarks_items[-1].bottomFrame = ttk.Frame(self.bookmarks_items[-1])
                        self.bookmarks_items[-1].bottomFrame.pack(side="top",fill="x")
                    elif bookmarksList[itemNumber]["type"]=="bookmark":
                        self.bookmarks_items[-1].iconImage = tkinter.PhotoImage(file=bookmarksList[itemNumber]["icon"] if os.path.exists(bookmarksList[itemNumber]["icon"]) else fileHandler.noIcon)
                        self.bookmarks_items[-1].iconLabel = ttk.Label(self.bookmarks_items[-1], text=bookmarksList[itemNumber]["title"], style="TButton", compound="left") ##TODO: add image=self.bookmarks_items[-1].iconImage, back
                        self.bookmarks_items[-1].iconLabel.pack(side="top", fill = "x")
                        self.bookmarks_items[-1].iconLabel.pack(side="top", fill = "x")
                        self.bookmarks_items[-1].bottomFrame = ttk.Frame(self.bookmarks_items[-1])
                        self.bookmarks_items[-1].bottomFrame.pack(side="top",fill="x")
                        self.bookmarks_items[-1].urlLabel = tkinter.Label(self.bookmarks_items[-1].bottomFrame,text=f"{bookmarksList[itemNumber]['url']}", font=("TkDefaultFont",10,"italic"))
                        self.bookmarks_items[-1].urlLabel.pack(side = "left")
                        self.bookmarks_items[-1].itemNumber = itemNumber
                        self.bookmarks_items[-1].bind("<Button-1>", lambda e, url=bookmarksList[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
                        self.bookmarks_items[-1].iconLabel.bind("<Button-1>",lambda e, url=bookmarksList[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
                        self.bookmarks_items[-1].bottomFrame.bind("<Button-1>", lambda e, url=bookmarksList[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
                    if self.searching:
                        self.searchRenderRunning = False
                    self.bookmarks_items[-1].pack(side = "top", anchor="w", fill="x")
            except IndexError:
                print("[Bookmarks] Ran out of bookmarks")
            self.progress.pack_forget()
            self.bookmarks_scrollbar.update()
            if not supressEventGeneration:
                self.bookmarks_list.event_generate("<<DoneLoading>>")
            self.currentlyLoadedItems=self.targetLoadedItems

    def loadTreeview(self,parent="",items=fileHandler.bookmarks,isFirst=True,parentText=""): # Recursively load all items.
        if isFirst:
            self.foldersDropdownOptions=["/"]
            for i in self.foldersList.get_children():
                self.foldersList.delete(i)
        for i in items:
                print(f"item type {i}")
                if i["type"] == "folder":
                    print(f"[Bookmarks] processing {i["title"]}")
                    newParentText= parentText+"/"+i['title']
                    self.foldersList.insert(parent,tkinter.END,iid=i,values=[i['title']],text=newParentText)
                    self.foldersDropdownOptions.append(newParentText) #Add folder item for folder select dropdowns
                    self.loadTreeview(i,i["items"],False,newParentText)
        self.foldersList.update()

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
        selected_folder_dict = self.foldersList.item(self.foldersList.focus()) #Blanked out until it isnt a problem
        print(selected_folder_dict)
        selected_folder = selected_folder_dict["text"]
        print(f"[Bookmarks] Jumping to folder: {selected_folder}")
        self.setUrl(f"flamingearth://bookmarks{selected_folder}")

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
                try:
                    if word in fileHandler.bookmarks[i]["title"] or word in fileHandler.bookmarks[i]["url"]:
                        self.foundIndicies.append(i)
                except KeyError:
                    if word in fileHandler.bookmarks[i]["title"]:
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
    
    def addBookmark(self,url=None,title=None,icon=None,edit=False,editIndex=None):
        self.addWindow = tkinter.Toplevel()
        self.addWindow.title("Add Bookmark")
        self.addWindow.geometry("300x200")
        self.titleText = tkinter.Label(self.addWindow,text="Title")
        self.titleText.pack(side="top")
        self.titleEntry = ttk.Entry(self.addWindow)
        self.titleEntry.pack(side="top")
        if title is not None:
            self.titleEntry.delete(0,tkinter.END)
            self.titleEntry.insert(0,string=title)
        self.urlVar = tkinter.StringVar(self.addWindow)
        if url is None:
            self.urlText = tkinter.Label(self.addWindow,text="URL")
            self.urlText.pack(side="top")
            self.urlEntry = ttk.Entry(self.addWindow,textvariable=self.urlVar)
            self.urlEntry.pack(side="top")
        else:
            self.urlVar.set(url)
        self.folderText = tkinter.Label(self.addWindow,text="Folder")
        self.folderText.pack(side="top")
        self.folderSelector = ttk.Combobox(self.addWindow,values=self.foldersDropdownOptions)
        self.folderSelector.pack(side="top")

        self.buttonFrame = ttk.Frame(self.addWindow,style="Card.TFrame")
        self.buttonFrame.pack(side="bottom", fill="x")

        self.saveButton = ttk.Button(self.buttonFrame, text="Save", style="Accent.TButton",command=self.saveBookmark)
        self.saveButton.pack(side="right")
        if edit==True:
            self.deleteButton = ttk.Button(self.buttonFrame,text="Delete")
            self.deleteButton.pack(side="right")
        self.cancelButton = ttk.Button(self.buttonFrame, text="Cancel", command=self.addWindow.destroy)
        self.cancelButton.pack(side="right")
    
    def addFolder(self,title=None,edit=False,editIndex=None):
        self.addFolderWindow = tkinter.Toplevel()
        self.addFolderWindow.title("Add Folder")
        self.addFolderWindow.geometry("300x200")
        self.folderTitleText = tkinter.Label(self.addFolderWindow,text="Title")
        self.folderTitleText.pack(side="top")
        self.folderTitleEntry = ttk.Entry(self.addFolderWindow)
        self.folderTitleEntry.pack(side="top")
        if title is not None:
            self.folderTitleEntry.delete(0,tkinter.END)
            self.folderTitleEntry.insert(0,string=title)
        self.folderText = tkinter.Label(self.addFolderWindow,text="Folder")
        self.folderText.pack(side="top")
        self.folderSelector = ttk.Combobox(self.addFolderWindow,values=self.foldersDropdownOptions)
        self.folderSelector.pack(side="top")

        self.buttonFrame = ttk.Frame(self.addFolderWindow,style="Card.TFrame")
        self.buttonFrame.pack(side="bottom", fill="x")

        self.saveButton = ttk.Button(self.buttonFrame, text="Save", style="Accent.TButton", command=self.saveFolder)
        self.saveButton.pack(side="right")
        if edit==True:
            self.deleteButton = ttk.Button(self.buttonFrame,text="Delete")
            self.deleteButton.pack(side="right")
        self.cancelButton = ttk.Button(self.buttonFrame, text="Cancel", command=self.addFolderWindow.destroy)
        self.cancelButton.pack(side="right")

    def saveBookmark(self):
        title = self.titleEntry.get()
        url = self.urlVar.get()
        folder = self.folderSelector.get()
        createFolder = False
        userAsked = False
        if folder not in self.foldersDropdownOptions:
            userAsked = True
            createFolder = messagebox.askyesno("Folder does not exist",f"The folder {folder} does not exist. Would you like to make it?")
        if createFolder == True:
            print("[BOOKMARKS] Folder being created")
        elif createFolder == False and userAsked:
            print("[BOOKMARKS] Bookmarks cannot be placed in a folder that doesn't exist.")
            self.addWindow.destroy()
            return
        self.addWindow.destroy()
    
    def saveFolder(self):
        title = self.folderTitleEntry.get()
        folder = self.folderSelector.get()
        createFolder = False
        userAsked = False
        if folder not in self.foldersDropdownOptions:
            createFolder = messagebox.askyesno("Folder does not exist",f"The folder {folder} does not exist. Would you like to make it?")
            userAsked = True
        if createFolder == True:
            print("[BOOKMARKS] Parent folders are being created")
        elif createFolder == False and userAsked:
            print("[BOOKMARKS] Folders cannot be placed in a folder that doesn't exist.")
            self.addWindow.destroy()
            return
        self.addFolderWindow.destroy()

class BookmarkBar:
    def __init__(self,tab):
        self = tkinter.Frame(tab)
        self.pack(fill = "x")