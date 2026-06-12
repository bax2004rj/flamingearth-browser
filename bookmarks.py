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
        self.rendering = False
        # Chunk limits
        self.currentlyLoadedItems = 0
        self.targetLoadedItems = 16
        self.iids = 0
        # Search
        self.foundIndicies = []

    def handle_scroll(self, y0, y1):
        self.bookmarks_scrollbar.set(y0,y1) # Set scrollbar length
        if float(y1)>0.9 and self.isEnabled and not self.searchRenderRunning and not self.rendering: # Load in next chunk of bookmarks
            print(f"[BOOKMARKS] New chunk loading, list length: {len(self.bookmarksList)}")
            newTargetLoadedItems = self.targetLoadedItems+16
            if newTargetLoadedItems>len(self.bookmarksList):
                self.targetLoadedItems = len(self.bookmarksList)
            else:
                self.targetLoadedItems = newTargetLoadedItems
            self.load_bookmarks(supressEventGeneration=True) # Load next chunk of bookmarks, but do not report it to tabFrame

    def load_bookmarks(self,supressEventGeneration = False):
        self.rendering = True
        self.bookmarksList = fileHandler.checkDirExistenceAndReturn(self.bookmarksURL)
        if len(self.bookmarksList) == 0 and not self.searching:
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
            progress_steps = 100 / len(self.bookmarksList)
            ##self.bookmarks_seperators.clear()
            ##self.bookmarks_items.clear()
            try:
                for i in range(self.targetLoadedItems-self.currentlyLoadedItems):
                    item = self.bookmarksList[int(i)+self.currentlyLoadedItems]
                    itemNumber = self.bookmarksList.index(item)
                    print(f"[Bookmarks] Processing item {item}, item number: {itemNumber}")
                    self.progress.step(progress_steps)

                    # Generate item frame
                    self.bookmarks_items.append(ttk.Frame(self.bookmarks_list,cursor="hand2"))
                    self.bookmarks_items[-1].itemNumber = itemNumber
                    if self.bookmarksList[itemNumber]["type"]=="folder":
                        self.bookmarks_items[-1].iconLabel = ttk.Label(self.bookmarks_items[-1], text=self.bookmarksList[itemNumber]["title"], style="TButton", compound="left") ##TODO: add image=self.bookmarks_items[-1].iconImage, back
                        self.bookmarks_items[-1].iconLabel.pack(side="top", fill = "x")
                        self.bookmarks_items[-1].bottomFrame = ttk.Frame(self.bookmarks_items[-1])
                        self.bookmarks_items[-1].bottomFrame.pack(side="top",fill="x")
                        self.bookmarks_items[-1].operationsMenu = tkinter.Menu(self.bookmarks_items[-1].bottomFrame)
                        self.bookmarks_items[-1].operationsMenu.add_command(label = "Edit",command = lambda title=self.bookmarksList[self.bookmarks_items[-1].itemNumber]["title"],path=self.bookmarksURL,edit=True,bookmark=self.bookmarksList[self.bookmarks_items[-1].itemNumber]: self.addFolder(title,edit,parentFolder=path,bookmark=bookmark))
                        self.bookmarks_items[-1].operationsMenu.add_command(label = "Delete",command = lambda path=f"{self.bookmarksURL}/{self.bookmarksList[self.bookmarks_items[-1].itemNumber]["title"]}",bookmark=self.bookmarksList[self.bookmarks_items[-1].itemNumber]: self.deleteBookmark(path,bookmark))
                        self.bookmarks_items[-1].operationsMenu.add_command(label = "Move",command = lambda path=f"{self.bookmarksURL}/{self.bookmarksList[self.bookmarks_items[-1].itemNumber]["title"]}",bookmark=self.bookmarksList[self.bookmarks_items[-1].itemNumber]: self.moveBookmark(path,bookmark))
                        self.bookmarks_items[-1].operationsMenu.add_command(label = "Copy",command = lambda path=f"{self.bookmarksURL}/{self.bookmarksList[self.bookmarks_items[-1].itemNumber]["title"]}",bookmark=self.bookmarksList[self.bookmarks_items[-1].itemNumber]: self.copyBookmark(path,bookmark))
                        self.bookmarks_items[-1].operationsButton=ttk.Menubutton(self.bookmarks_items[-1].bottomFrame,menu=self.bookmarks_items[-1].operationsMenu,text="≡")
                        self.bookmarks_items[-1].operationsButton.pack(side="right")
                        self.bookmarks_items[-1].bind("<Button-1>", lambda e, url=f"{self.bookmarksURL}/{self.bookmarksList[self.bookmarks_items[-1].itemNumber]["title"]}": self.setUrl(url))
                        self.bookmarks_items[-1].iconLabel.bind("<Button-1>", lambda e, url=f"{self.bookmarksURL}/{self.bookmarksList[self.bookmarks_items[-1].itemNumber]["title"]}": self.setUrl(url))
                        self.bookmarks_items[-1].bottomFrame.bind("<Button-1>", lambda e, url=f"{self.bookmarksURL}/{self.bookmarksList[self.bookmarks_items[-1].itemNumber]["title"]}": self.setUrl(url))
                    elif self.bookmarksList[itemNumber]["type"]=="bookmark":
                        self.bookmarks_items[-1].iconImage = tkinter.PhotoImage(file=self.bookmarksList[itemNumber]["icon"] if os.path.exists(self.bookmarksList[itemNumber]["icon"]) else fileHandler.noIcon)
                        self.bookmarks_items[-1].iconLabel = ttk.Label(self.bookmarks_items[-1], text=self.bookmarksList[itemNumber]["title"], style="TButton", compound="left") ##TODO: add image=self.bookmarks_items[-1].iconImage, back
                        self.bookmarks_items[-1].iconLabel.pack(side="top", fill = "x")
                        self.bookmarks_items[-1].bottomFrame = ttk.Frame(self.bookmarks_items[-1])
                        self.bookmarks_items[-1].bottomFrame.pack(side="top",fill="x")
                        self.bookmarks_items[-1].urlLabel = tkinter.Label(self.bookmarks_items[-1].bottomFrame,text=f"{self.bookmarksList[itemNumber]['url']}", font=("TkDefaultFont",10,"italic"))
                        self.bookmarks_items[-1].urlLabel.pack(side = "left")
                        self.bookmarks_items[-1].operationsMenu = tkinter.Menu(self.bookmarks_items[-1].bottomFrame)
                        self.bookmarks_items[-1].operationsMenu.add_command(label = "Edit",command = lambda url=self.bookmarksList[self.bookmarks_items[-1].itemNumber]["url"],title=self.bookmarksList[self.bookmarks_items[-1].itemNumber]["title"],icon=self.bookmarksList[self.bookmarks_items[-1].itemNumber]["icon"],path=self.bookmarksURL,edit=True, bookmark=self.bookmarksList[self.bookmarks_items[-1].itemNumber]: self.addBookmark(url,title,icon,edit,parentFolder=path,bookmark=bookmark))
                        self.bookmarks_items[-1].operationsMenu.add_command(label = "Delete",command = lambda path=f"{self.bookmarksURL}/{self.bookmarksList[self.bookmarks_items[-1].itemNumber]["title"]}",bookmark=self.bookmarksList[self.bookmarks_items[-1].itemNumber]: self.deleteBookmark(path,bookmark))
                        self.bookmarks_items[-1].operationsMenu.add_command(label = "Move",command = lambda path=f"{self.bookmarksURL}/{self.bookmarksList[self.bookmarks_items[-1].itemNumber]["title"]}",bookmark=self.bookmarksList[self.bookmarks_items[-1].itemNumber]: self.moveBookmark(path,bookmark))
                        self.bookmarks_items[-1].operationsMenu.add_command(label = "Copy",command = lambda path=f"{self.bookmarksURL}/{self.bookmarksList[self.bookmarks_items[-1].itemNumber]["title"]}",bookmark=self.bookmarksList[self.bookmarks_items[-1].itemNumber]: self.copyBookmark(path,bookmark))
                        self.bookmarks_items[-1].operationsButton=ttk.Menubutton(self.bookmarks_items[-1].bottomFrame,menu=self.bookmarks_items[-1].operationsMenu,text="≡")
                        self.bookmarks_items[-1].operationsButton.pack(side="right")
                        self.bookmarks_items[-1].bind("<Button-1>", lambda e, url=self.bookmarksList[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
                        self.bookmarks_items[-1].iconLabel.bind("<Button-1>",lambda e, url=self.bookmarksList[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
                        self.bookmarks_items[-1].urlLabel.bind("<Button-1>", lambda e, url=self.bookmarksList[self.bookmarks_items[-1].itemNumber]["url"]: self.setUrl(url))
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
            self.rendering = False

    def loadTreeview(self,parent="",items=fileHandler.bookmarks,isFirst=True,parentText=""): # Recursively load all items.
        if isFirst:
            self.iids=0
            self.foldersDropdownOptions=["/"]
            for i in self.foldersList.get_children():
                self.foldersList.delete(i)
            self.foldersList.insert("",tkinter.END,iid=self.iids,values="All Bookmarks",text="")
            self.iids=+1
        for i in items:
                print(f"item type {i['type']}")
                if i['type'] == "folder":
                    self.iids+=1
                    print(f"[Bookmarks] processing {i['title']},iid: {self.iids}")
                    newParentText= parentText+"/"+i['title']
                    self.foldersList.insert(parent,tkinter.END,iid=self.iids,values=[i['title']],text=newParentText)
                    self.foldersDropdownOptions.append(newParentText) #Add folder item for folder select dropdowns
                    self.loadTreeview(self.iids,i['items'],False,newParentText)
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
        if url == "flamingearth://bookmarks/": # Rewrite so both "/" and "" paths work.
            url = "flamingearth://bookmarks"
        self.bookmarksURL = url
        print(f"[Bookmarks] URL set to {self.bookmarksURL}")
        self.bookmarks_list.event_generate("<<BookmarksURLClicked>>")

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
        selected_folder_dict = self.foldersList.item(self.foldersList.focus())
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
    
    def addBookmark(self,url=None,title=None,icon=None,edit=False,editIndex=None,parentFolder = "/",bookmark=None):
        parentFolder = parentFolder.lstrip("flamingearth://bookmarks")
        self.addWindow = tkinter.Toplevel()
        if edit:
            self.addWindow.title("Edit Bookmark")
            # Collect old title and type so old data can be deleted.
            self.oldTitle = title
            self.oldType = "bookmark"
            self.oldPath = parentFolder
        else:
            self.addWindow.title("Add Bookmark")
        self.addWindow.geometry("600x400")
        self.titleText = tkinter.Label(self.addWindow,text="Title")
        self.titleText.pack(side="top")
        self.titleEntry = ttk.Entry(self.addWindow)
        self.titleEntry.pack(side="top")
        if title is not None:
            self.titleEntry.delete(0,tkinter.END)
            self.titleEntry.insert(0,string=title)
        self.urlVar = tkinter.StringVar(self.addWindow)
        self.urlText = tkinter.Label(self.addWindow,text="URL")
        self.urlText.pack(side="top")
        self.urlEntry = ttk.Entry(self.addWindow,textvariable=self.urlVar)
        self.urlEntry.pack(side="top")
        if url is not None:
            self.urlVar.set(url)
        self.folderText = tkinter.Label(self.addWindow,text="Folder")
        self.folderText.pack(side="top")
        self.fsVar = tkinter.StringVar(self.addWindow,parentFolder)
        self.folderSelector = ttk.Combobox(self.addWindow,values=self.foldersDropdownOptions,textvariable=self.fsVar)
        self.folderSelector.pack(side="top")
        self.buttonFrame = ttk.Frame(self.addWindow,style="Card.TFrame")
        self.buttonFrame.pack(side="bottom", fill="x")

        self.saveButton = ttk.Button(self.buttonFrame, text="Save", style="Accent.TButton",command=self.saveBookmark)
        self.saveButton.pack(side="right")
        if edit==True:
            self.deleteButton = ttk.Button(self.buttonFrame,text="Delete",command = lambda path = parentFolder,bookmark=bookmark:self.deleteBookmark(path,bookmark,True,False))
            self.deleteButton.pack(side="right")
        self.cancelButton = ttk.Button(self.buttonFrame, text="Cancel", command=self.addWindow.destroy)
        self.cancelButton.pack(side="right")
    
    def addFolder(self,title=None,edit=False,editIndex=None,parentFolder = "/",bookmark=None):
        parentFolder = parentFolder[24:]
        self.addFolderWindow = tkinter.Toplevel()
        if edit:
            self.addFolderWindow.title("Edit Folder")
            # Collect old title and type so old data can be deleted.
            self.oldTitle = title
            self.oldType = "folder"
            self.oldPath = parentFolder
            self.oldData = bookmark["items"]
        else:
            self.addFolderWindow.title("Add Folder")
        self.addFolderWindow.geometry("600x400")
        self.folderTitleText = tkinter.Label(self.addFolderWindow,text="Title")
        self.folderTitleText.pack(side="top")
        self.folderTitleEntry = ttk.Entry(self.addFolderWindow)
        self.folderTitleEntry.pack(side="top")
        if title is not None:
            self.folderTitleEntry.delete(0,tkinter.END)
            self.folderTitleEntry.insert(0,string=title)
        self.folderText = tkinter.Label(self.addFolderWindow,text="Folder")
        self.folderText.pack(side="top")
        self.fsVar = tkinter.StringVar(self.addFolderWindow,parentFolder)
        self.folderSelector = ttk.Combobox(self.addFolderWindow,values=self.foldersDropdownOptions,textvariable=self.fsVar)
        self.folderSelector.pack(side="top")

        self.buttonFrame = ttk.Frame(self.addFolderWindow,style="Card.TFrame")
        self.buttonFrame.pack(side="bottom", fill="x")

        self.saveButton = ttk.Button(self.buttonFrame, text="Save", style="Accent.TButton", command=lambda editSave=edit,:self.saveFolder(editSave))
        self.saveButton.pack(side="right")
        if edit==True:
            self.deleteButton = ttk.Button(self.buttonFrame,text="Delete",command = lambda path = parentFolder,bookmark=bookmark:self.deleteBookmark(path,bookmark,True,True))
            self.deleteButton.pack(side="right")
        self.cancelButton = ttk.Button(self.buttonFrame, text="Cancel", command=self.addFolderWindow.destroy)
        self.cancelButton.pack(side="right")

    def saveBookmark(self,edit=False):
        if edit: #Delete and re-add with new data.
            fileHandler.deleteBookmarks(self.oldTitle,"bookmark",self.oldPath)
        title = self.titleEntry.get()
        url = self.urlVar.get()
        folder = self.folderSelector.get()
        icon = os.path.join(fileHandler.iconFolderPNG,"noIconPage.png")# TODO: allow user to set icon/use website icon.
        createFolder = False
        userAsked = False
        if title == None or title == "":
            title = "Untitled"
        if url == None or url == "":
            messagebox.showerror("No URL","No URL was provided, please provide one and try again")
            return
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
        # Save data
        saveJson = {
                'title': title,
                'type': "bookmark",
                'icon': icon,
                'url': url,
        }
        fileHandler.appendBookmarks(saveJson,folder)
        # Reload Bookmarks viewer
        self.setUrl(f"flamingearth://bookmarks{folder}")

    def saveFolder(self,edit=False):
        if edit: #Delete and re-add with new data.
            fileHandler.deleteBookmarks(self.oldTitle,"folder",self.oldPath)
        title = self.folderTitleEntry.get()
        folder = self.folderSelector.get()
        if self.oldData is None:
            data = []
        else:
            data = self.oldData
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
        saveJson = {
                'title': title,
                'type': "folder",
                'items': data,
        }
        fileHandler.appendBookmarks(saveJson,folder)
        # Reload Bookmarks viewer and treeview/dropdown
        self.loadTreeview(parent="",items=fileHandler.bookmarks,isFirst=True)
        self.setUrl(f"flamingearth://bookmarks{folder}")

    def deleteBookmark(self,path,bookmark,fromEdit=False,folderDelete=False):
        print(path)
        path = path[25:].rstrip(f"/{bookmark["title"]}")
        # Destroy edit window if from edit window
        if fromEdit and not folderDelete:
            self.addWindow.destroy()
        elif fromEdit and folderDelete:
            self.addFolderWindow.destroy()
        confirmation = messagebox.askyesno("Confirm deletion","Are you sure you want to delete this item? You cannot get it back after deletion.")
        out=-1
        if confirmation:
            out=fileHandler.deleteBookmarks(bookmark["title"],bookmark["type"],path)
        print(out)
        # Reload Bookmarks viewer and treeview/dropdown
        if out==0:
            self.loadTreeview(parent="",items=fileHandler.bookmarks,isFirst=True)
            self.setUrl(f"flamingearth://bookmarks/{path}")

    def moveBookmark(self,path,bookmark):
        self.path = path[25:]
        self.data = bookmark
        self.moveFolderWindow = tkinter.Toplevel()
        self.moveFolderWindow.title("Move Item")
        self.moveFolderWindow.geometry("300x200")
        self.folderText = tkinter.Label(self.moveFolderWindow,text="Move item to folder:")
        self.folderText.pack(side="top")
        self.fsVar = tkinter.StringVar(self.moveFolderWindow,"/")
        self.folderSelector = ttk.Combobox(self.moveFolderWindow,values=self.foldersDropdownOptions,textvariable=self.fsVar)
        self.folderSelector.pack(side="top")

        self.buttonFrame = ttk.Frame(self.moveFolderWindow,style="Card.TFrame")
        self.buttonFrame.pack(side="bottom", fill="x")

        self.saveButton = ttk.Button(self.buttonFrame, text="Move", style="Accent.TButton", command=self.moveObject)
        self.saveButton.pack(side="right")
        self.cancelButton = ttk.Button(self.buttonFrame, text="Cancel", command=self.moveFolderWindow.destroy)
        self.cancelButton.pack(side="right")

    def moveObject(self):
        fileHandler.deleteBookmarks(self.data["title"],self.data["type"],self.path)
        newPath = self.fsVar.get()
        fileHandler.appendBookmarks(self.data,newPath)
        self.moveFolderWindow.destroy()
        # Reload Bookmarks viewer and treeview/dropdown
        self.loadTreeview(parent="",items=fileHandler.bookmarks,isFirst=True)
        self.setUrl(f"flamingearth://bookmarks{newPath}")

    def copyBookmark(self,path,bookmark):
        self.parentFolder = path[25:]
        self.data = bookmark
        self.copyFolderWindow = tkinter.Toplevel()
        self.copyFolderWindow.title("Copy Item")
        self.copyFolderWindow.geometry("300x200")
        self.folderText = tkinter.Label(self.copyFolderWindow,text="Copy item to folder:")
        self.folderText.pack(side="top")
        self.fsVar = tkinter.StringVar(self.copyFolderWindow,"/")
        self.folderSelector = ttk.Combobox(self.copyFolderWindow,values=self.foldersDropdownOptions,textvariable=self.fsVar)
        self.folderSelector.pack(side="top")

        self.buttonFrame = ttk.Frame(self.copyFolderWindow,style="Card.TFrame")
        self.buttonFrame.pack(side="bottom", fill="x")

        self.saveButton = ttk.Button(self.buttonFrame, text="Copy", style="Accent.TButton", command=self.copyObject)
        self.saveButton.pack(side="right")
        self.cancelButton = ttk.Button(self.buttonFrame, text="Cancel", command=self.copyFolderWindow.destroy)
        self.cancelButton.pack(side="right")

    def copyObject(self):
        newPath = self.fsVar.get()
        fileHandler.appendBookmarks(self.data,newPath)
        self.copyFolderWindow.destroy()
        # Reload Bookmarks viewer and treeview/dropdown
        self.loadTreeview(parent="",items=fileHandler.bookmarks,isFirst=True)
        self.setUrl(f"flamingearth://bookmarks{newPath}")

class BookmarkBar:
    def __init__(self,tab):
        self = tkinter.Frame(tab)
        self.pack(fill = "x")
