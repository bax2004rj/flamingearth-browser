# flamingearth-browser
[![License](https://img.shields.io/:license-gplv2-green.svg)](https://tldrlegal.com/license/gnu-general-public-license-v2)

A web browser written in Python using Tkinter, and the [TkinterWeb](https://github.com/Andereoo/TkinterWeb) module. Themes are currently provided by the [Sun Valley TTK/TCL theme](https://github.com/rdbende/Sun-Valley-ttk-theme). It is vey basic, and due to its use of TkinterWeb, it does not completely support JS elements, so it is not currently reccomended as a daily-use browser
![Screenshot_20220619_225428](https://user-images.githubusercontent.com/40148394/174517065-54689d3c-a0f1-4fbd-b004-14752caad360.png "yes this image is very old, probably going to fix this when the package is released")

## Features
- Lightweight browser
- Intuitive UI

## Contributing
Anyone is welcome to help out. Currently, we are open to help with development work. If you would like to help, please check [Issues](https://github.com/bax2004rj/flamingearth-browser/issues) so you can get ideas where help is needed. If there is an issue you find with the code, don't hesitate to add it to [Issues](https://github.com/bax2004rj/flamingearth-browser/issues). The software probably has a ton of bugs I missed, so any issues are welcomed.

## Installation
This software is currently a collection of python scripts, so running from code should work for all OSes. Obviously, make sure you have python 
### Prerequisites
- python
- tkinter (Some Linux distros don't include it as standard python, make sure you have it)
- sv_ttk
- tkinterweb
- darkdetect
- humanize
- tkcalendar
- pillow
- pythonmonkey
#### Prerequisites specific to Windows
- pywinstyles

### Install instructions (from source, all operating systems)
- If you don't have python already, install it.
    - Also make sure to get PIP, so you can get prerequisites
- Clone the Github repo
    - If you have Git, run ``git clone github.com/bax2004rj/flamingearth-browser``
    - If not, use the "download zip" button on github.
-  Install all prerequisites. In future, we might bundle a script that automates this for you.
    - Run ``pip install sv_ttk tkinterweb darkdetect humanize tkcalendar pillow pythonmonkey`` in a terminal.
    - On Windows, run ``pip install sv_ttk tkinterweb darkdetect humanize tkcalendar pillow pythonmonkey pywinstyles``
    - If your system gives issues regarding ``externally-managed-environments``, the developers of your OS probably want you to install everything off their package manager. Check your operating systems package manager to find these pacakges. For the packages you cannot find on your package manager, run PIP again, removing the names of packages you already have, and add ``--break-system-packages`` to the end of it.
> [!NOTE]
> Generally, package mangers that do this title python packages as ``python3-<packageName>``

- On some installs on Windows, pythonmonkey failed to install as it was looking for npm. Try installing that if that error occurs.
## Usage
- Move to the directory where the code cloned to. 
- Run ``main.py``.
> [!NOTE]
> If using a file manager to navigate the code, python might let you double-click ``main.py`` to run the code.

## Credits
Thanks to the [TkinterWeb](https://github.com/Andereoo/TkinterWeb) project for making the core of this web browser. 
Thanks to the other packages featured here.
Special thanks to any contributors who help out on the project.
