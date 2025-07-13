import os
import darkdetect
import json

## Get icon file locations
cwd = os.getcwd()
iconFolderPNG = os.path.join(cwd,"icons","png")
iconFolderSVG = os.path.join(cwd,"icons","png")

# Files
noIcon = os.path.join(iconFolderPNG,"noIconPage.png")
noShortcut = os.path.join(iconFolderPNG,"noShortcut.png")

# App data 
# Detect host os
if os.name == 'nt':  # Windows
    appData = os.path.join(os.getenv('APPDATA'), 'flamingearth')
elif os.name == 'posix':  # Unix-like (Linux, macOS)
    appData = os.path.join(os.path.expanduser('~'), '.flamingearth')
else:  # Fallback for other OS types
    appData = os.path.join(os.getcwd(),"flamingearthData")
# Settings file
settingsFile = os.path.join(appData,"settings.json") 
# history file
historyFile = os.path.join(appData,"history.json")
historyIconsFile = os.path.join(appData,"historyIcons") 
# bookmarks file
bookmarksFile = os.path.join(appData,"bookmarks.json") 
bookmarksIconsFile = os.path.join(appData,"bookmarksIcons")
# downloads file
downloadsFile = os.path.join(appData,"downloads.json") 


#Setting variables

# UI/UX settings
autodark = True # Automatically detect dark mode
darkmode = False # Dark mode autodetect by default
tkinterTheme = "sv_ttk" # Theme for tkinter, sv_ttk is the default

displayBookmarks = True # Display bookmarks in the address bar
notifyForTabsOnQuit = 0 # Notify user if tabs are open on quit. -1 = no notification, 0 = always ask, 1 <= ask if there are more tabs open than threshold  

newtabDisplayMode = "mostVisited" 
newtabItems = 8

browserFlags = []

homepage = "flamingearth://newtab"
historyURL = [] # History URL list
historyTitles = [] # History titles list
historyIcons = [] # History icons list (locations to icon files)
historyTimeAccessed = [] # History date accessed list
bookmarks = [] # Bookmarks url list
bookmarksTitles = [] # Bookmarks titles list
bookmarksIcons = [] # Bookmarks icons list (locations to icon files)
downloads = [] # Downloads list
downloadTime = [] # Downloads date list
downloadSource = [] # Downloads source list


def loadSettings():
    global autodark, darkmode, history, historyDateAccessed, downloads, bookmarks, settingsFile, homepage, notifyForTabsOnQuit, tkinterTheme, displayBookmarks, newtabDisplayMode, newtabItems, browserFlags
    # Create appdata directory if it doesn't exist
    if not os.path.exists(appData):
        os.makedirs(appData)
    # Load settings from file
    if os.path.exists(settingsFile):
        print ("[FILEHANDLER] Settings file found, loading settings...")
        with open(settingsFile, 'r') as file:
            settings = json.load(file)
            autodark = settings.get('autodark', True)
            darkmode = settings.get('darkmode', False)
            tkinterTheme = settings.get('tkinterTheme', 'sv_ttk')
            displayBookmarks = settings.get('displayBookmarks', True)
            notifyForTabsOnQuit = settings.get('notifyForTabsOnQuit', 0)
            newtabDisplayMode = settings.get('newtabDisplayMode', 'mostVisited')
            newtabItems = settings.get('newtabItems', 8)
            browserFlags = settings.get('browserFlags', [])
            homepage = settings.get('homepage', 'flamingearth://newtab')
            print("[FILEHANDLER] Settings loaded successfully.")
    else:
        # If settings file does not exist, create default settings
        print ("[FILEHANDLER] Settings file not found, creating default settings...")
        settings = {
            'autodark': autodark,
            'darkmode': darkmode,
            'tkinterTheme': tkinterTheme,
            'displayBookmarks': displayBookmarks,
            'notifyForTabsOnQuit': notifyForTabsOnQuit,
            'newtabDisplayMode': newtabDisplayMode,
            'newtabItems': newtabItems,
            'browserFlags': browserFlags,
            'homepage': homepage
        }
        with open(settingsFile, 'w') as file:
            json.dump(settings, file, indent=4)
    #Set darkmode based on settings file
    if autodark == True:
           print("[FILEHANDLER] Autodark is enabled, checking dark mode...")
           darkmode = darkdetect.isDark() # Check if dark mode is enabled
           print("[FILEHANDLER] Dark mode is set to:", darkmode)
    
def loadHistory():
    global historyFile,historyURL,historyTitles,historyIcons, historyTimeAccessed
    if os.path.exists(historyFile):
        with open(historyFile, 'r') as file:
            historyJson = json.load(file)
            historyURL = historyJson.get('historyURL', [])
            historyTitles = historyJson.get('historyTitles',[])
            historyIcons = historyJson.get('historyIcons', [])
            historyTimeAccessed = historyJson.get('historyTimeAccessed', [])
    else:
        historyFileOut = {
            'historyURL': historyURL,
            'historyTitles': historyTitles,
            'historyIcons': historyIcons,
            'historyTimeAccessed': historyTimeAccessed,
        }
        with open(historyFile, 'w') as file:
            json.dump(historyFileOut, file, indent=4)

def loadBookmarks():
    global bookmarksFile,bookmarks,bookmarksTitles,bookmarksIcons
    if os.path.exists(bookmarksFile):
        with open(bookmarksFile, 'r') as file:
            bookmarksJson = json.load(file)
            bookmarks = bookmarksJson.get('bookmarks', [])
            bookmarksTitles = bookmarksJson.get('bookmarksTitles', [])
            bookmarksIcons = bookmarksJson.get('bookmarksIcons', [])
    else:
        bookmarksFileOut = {
            'bookmarks': bookmarks,
            'bookmarksTitles': bookmarksTitles,
            'bookmarksIcons': bookmarksIcons,
        }
        with open(bookmarksFile, 'w') as file:
            json.dump(bookmarksFileOut, file, indent=4)

def loadDownloads():
    global downloadsFile,downloads,downloadTime,downloadSource
    if os.path.exists(downloadsFile):
        with open(downloadsFile, 'r') as file:
            downloadsJson = json.load(file)
            downloads = downloadsJson.get('downloads', [])
            downloadTitles = downloadsJson.get('downloadTitles', [])
            downloadIcons = downloadsJson.get('downloadIcons', [])
    else:
        downloadsFileOut = {
            'downloads': downloads,
            'downloadTitles': downloadTime,
            'downloadIcons': downloadSource,
        }
        with open(downloadsFile, 'w') as file:
            json.dump(downloadsFileOut, file, indent=4)

def saveSettings():
    global autodark, darkmode, settingsFile, homepage, notifyForTabsOnQuit, tkinterTheme, displayBookmarks, newtabDisplayMode, newtabItems, browserFlags
    settings = {
        'autodark': autodark,
        'darkmode': darkmode,
        'tkinterTheme': tkinterTheme,
        'displayBookmarks': displayBookmarks,
        'notifyForTabsOnQuit': notifyForTabsOnQuit,
        'newtabDisplayMode': newtabDisplayMode,
        'newtabItems': newtabItems,
        'browserFlags': browserFlags,
        'homepage': homepage
    }
    with open(settingsFile, 'w') as file:
        json.dump(settings, file, indent=4)
    print("[FILEHANDLER] Settings saved successfully.")

def saveHistory():
    global historyFile,historyURL,historyTitles,historyIcons,historyTimeAccessed
    historyFileOut = {
        'historyURL': historyURL,
        'historyTitles': historyTitles,
        'historyIcons': historyIcons,
        'historyTimeAccessed': historyTimeAccessed,
    }
    with open(historyFile, 'w') as file:
        json.dump(historyFileOut, file, indent=4)

def saveBookmarks():
    global bookmarksFile,bookmarks,bookmarksTitles,bookmarksIcons
    bookmarksFileOut = {
        'bookmarks': bookmarks,
        'bookmarksTitles': bookmarksTitles,
        'bookmarksIcons': bookmarksIcons,
    }
    with open(bookmarksFile, 'w') as file:
        json.dump(bookmarksFileOut, file, indent=4)

def saveDownloads():
    global downloadsFile,downloads,downloadTime,downloadSource
    downloadsFileOut = {
        'downloads': downloads,
        'downloadTitles': downloadTime,
        'downloadIcons': downloadSource,
    }
    with open(downloadsFile, 'w') as file:
        json.dump(downloadsFileOut, file, indent=4)

def saveIcon(image_data):
    global historyIconsFile
    saveLocation = os.path.join(historyIconsFile,f"{len(historyIcons)}.png")
    with open(saveLocation, 'wb') as icon_file:
        icon_file.write(image_data)
    print("[FILEHANDLER] Icon saved successfully.")
    return saveLocation
    