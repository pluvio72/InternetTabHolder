import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QColor, QIcon
from constants import tabCount, tabRows, tabList, IMAGE_WIDTH, IMAGE_HEIGHT, ASPECT_RATIO, MIN_TAB_WIDTH, MIN_TAB_HEIGHT, ABSOLUTE_IMAGE_FOLDER_PATH, IMAGE_FOLDER_PATH
from droparea import DropArea
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class DropSiteWindow(QWidget):
    def __init__(self):
        super().__init__()

        ###
        ### ADD SUPPORT FOR MULTIPLE PAGES OF TABS AND NAME THEM??
        ### QUICK START IN OPTIONS OR CHANGE OPTIONS TO FILE MENU
        ### ADD OPTIONS TO CHANGE TABS PER ROW?
        ### DONT DELETE PREVIOUSLY DELETED TABS KEEP IMAGE FILE IN _NAME AND _TABLIST CAN BE SHOWN IN MANUAL TAB ADD DIALOG
        ### RETHINK WHETHER YOU HAVE EMPTY TAB AS DROP AREA OR WHOLE WINDOW AS DROP AREA
        ### FAVOURITE TABS HIGHER
        ### SUPPORT MULTIPLE OTHER DATA TYPES E.G. PDF OPENS IN PDF VIEWER
        ### REORDER TABS VERTICALLY????
        ### MAYBE RUN CHECK WITH OS.POPEN IF CHROMEDRIVER INSTANCES ARE MORE THEN 5 OR SO AND KILL THEM
        ###

        # SETUP THUMBNAIL FOLDER 
        if not (os.path.isdir(ABSOLUTE_IMAGE_FOLDER_PATH)): os.mkdir(ABSOLUTE_IMAGE_FOLDER_PATH)

        self.clearingTabs = False
        self.acceptDrops = True

        # SETUP HEADLESS CHROME DRIVER -> SETS IMAGE RESOLUTION (BROWSER_SIZE)
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options, executable_path='./chromedriver_77')
        self.driver.set_window_size(IMAGE_WIDTH, IMAGE_HEIGHT)

        # SETUP LAYOUTS
        self.mainLayout = QVBoxLayout()
        self.scroll = QScrollArea()
        self.scrollWidget = QWidget()
        self.scrollWidgetLayout = QVBoxLayout()
        
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setFrameStyle(QFrame.NoFrame)

        self.scrollWidgetLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scrollWidgetLayout.setContentsMargins(3, 3, 3, 3)
        self.scrollWidgetLayout.setSpacing(3)

        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.scroll.setWidget(self.scrollWidget)
        self.mainLayout.addWidget(self.scroll)
        self.setLayout(self.mainLayout)

        # IF TAB FILE EXISTS REMAKE TABS
        path = os.path.join(os.getcwd(), 'tabs.txt')
        exists = os.path.isfile(path)
        size = 0
        if exists: size = os.path.getsize(path)
        if size > 0 and exists:
            self.loadTabs(path)
        else: self.newTab(False)
    
    def loadTabs(self, path):
        with open(path, 'r') as f:
            data = f.readlines()
            for index, line in enumerate(data):
                l = line.split('\n')[0]
                currentItems = l.split(' ')
                url = currentItems[0]
                imagePath = currentItems[1]
                tabNumber = currentItems[2]
                # IF ITS LAST TAB ADD EMPTY TAB AFTER
                if index == len(data)-1:
                    self.newTab(True, url, imagePath, True)
                else:
                    self.newTab(True, url, imagePath, False)

    def newTab(self, load=False, url=None, imagePath=None, addTabAfter=False):
        global tabCount
        if (tabCount % 3) == 0:
            self.currentRow = QHBoxLayout()
            self.currentRow.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.currentRow.setSpacing(3)
            self.currentRow.setSizeConstraint(QLayout.SetMinimumSize)
            self.scrollWidgetLayout.insertLayout(self.scrollWidgetLayout.layout().count(), self.currentRow)
            tabRows.append(self.currentRow)

        tabCount += 1
        drp = DropArea(tabCount, self.driver, MIN_TAB_WIDTH, MIN_TAB_HEIGHT, ASPECT_RATIO, ABSOLUTE_IMAGE_FOLDER_PATH)
        drp.imageLoaded.connect(self.newTab)
        drp.tabDeleted.connect(lambda: self.deleteTab(drp))
        drp.tabAdded.connect(self.addTabToList)
        drp.tabReordered.connect(self.reorderTab)
        drp.destroyed.connect(self.reorganizeTabList)
        self.currentRow.addWidget(drp)

        # IF ITS A NEW TAB LOAD IAMGE AND URL
        if load: drp.load(url, imagePath, addTabAfter)

    def deleteTab(self, tab):
        global tabCount
        if tabCount == 1:
            tab.taken = False
            tab.clear()
        else:
            tabCount -= 1
            tabList.remove(tab)
            tab.setParent(None) 
            tab.deleteLater()

        # REMOVE ENTRY FROM SAVED TABS FILE
        fileData = []
        with open('tabs.txt', 'r') as inp:
            fileData = inp.readlines()

        # CHECK IF THERE IS DUPLICATE TAB IF SO DON'T DELETE IMAGE
        archiveImage = True
        for tabItem in tabList:
            if tabItem.url == tab.url:
                archiveImage = False

        with open('tabs.txt', 'w') as out:
            for line in fileData:
                # CURRENT ITEMS LAYOUT -> (URL IMAGE_PATH TAB_NUMBER)
                currentItems = line.split(' ')
                tabNum = int(currentItems[2])
                if not (tabNum == tab.tabNumber): 
                    out.write(line)
                else: 
                    if archiveImage:
                        try: 
                            #os.remove(os.path.join(IMAGE_FOLDER_PATH, currentItems[1]))
                            os.rename(os.path.join(IMAGE_FOLDER_PATH, currentItems[1]), os.path.join(IMAGE_FOLDER_PATH, '.' + currentItems[1]))
                        except FileNotFoundError: print('File Not Found:::' + currentItems[1])
        
        if archiveImage:
            # APPEND URL TO FILE AND CHECK IF THERE ARE OVER 20 ENTRIED IF SO REMOVE ONE ENTRY
            with open('.tabs.txt', 'a+') as f:
                f.seek(0)
                lines = f.readlines()
                if len(lines) > 20:
                    f.seek(0)
                    f.truncate(0)
                    for i in range(1, len(lines)):
                        f.write(lines[i])
                # CHECK FOR DUPLICATE
                duplicate = False
                for line in lines:
                    if line.split(' ')[0] == tab.url:
                        duplicate = True
                if not duplicate:
                    f.write(tab.url + ' ' + '.' + tab.imagePath + '\n')


    def addTabToList(self, tab, tabNo):
        global tabList
        if len(tabList) <= tabNo:
            tabList.append(tab)
        else:
            tabList[tabNo] = tab
    
    def reorderTab(self, tab, swapValue):
        global tabList
        index = tabList.index(tab)
        # SWAP VALUE = SHIFT IN TABS E.G. -1 FOR ONE LEFT
        newIndex = index + swapValue
        tabList.remove(tab)
        tabList.insert(newIndex, tab)
        self.reorganizeTabList()

    def reorganizeTabList(self):
        global tabList
        global tabRows

        path = os.path.join(os.getcwd(), 'tabs.txt')
        exists = os.path.isfile(path)
        size = 0
        if exists: size = os.path.getsize(path)
        if size > 0 and exists:
            if not self.clearingTabs:
                for index, tab in enumerate(tabList):
                    #TAB NUMBERS START AT 1
                    tab.tabNumber = index+1

                # REORDER TABS IN THE SAVED TABS FILE SO THEY HAVE CORRECT TAB NUMBER
                with open('tabs.txt', 'r+') as f:
                    lines = f.readlines()
                    currentTab = 1
                    finalStringData = ''
                    for line in lines:
                        l = line.split('\n')[0]
                        currentItems = l.split(' ')
                        currentString = ''
                        # REORGANIZING AFTER DELETING A TAB
                        if(currentTab != int(currentItems[2])):
                            currentString += currentItems[0] + ' ' + tabList[currentTab-1].imagePath + ' ' + str(currentTab) + '\n'
                        # REORGANIZING AFTER REORDERING A TAB
                        elif(currentItems[0] != tabList[currentTab-1].url):
                            current = tabList[currentTab-1]
                            currentString += current.url + ' ' + current.imagePath + ' ' + str(current.tabNumber) + '\n'
                        else:
                            currentString += line
                        currentTab += 1
                        finalStringData += currentString

                    # SEEK BEGINNING -> CLEAR FILE -> WRITE DATA (TRUNCATE SETS FILE SIZE TO MAX (0))
                    f.seek(0)
                    f.truncate(0)
                    f.write(finalStringData)
                
                #IF ANY LAYOUTS HAVE < 3 CHILDREN REORGANIZE THE WIDGETS
                complete = False
                while not complete:
                    for i in range(0, len(tabRows)-1):
                        if tabRows[i].count() < 3:
                            child = tabRows[i + 1].itemAt(0)
                            tabRows[i + 1].removeItem(child)
                            tabRows[i].addItem(child)
                    complete = True
                
                # IF CURRENT ROW HAS NO CHILDREN REMOVE IT AND SET IT TO PREVIOUS ROW
                if self.currentRow.count() == 0:
                    tabRows.remove(self.currentRow)
                    self.currentRow.deleteLater()
                    self.currentRow = tabRows[len(tabRows)-1]

    def clearTabs(self):
        global tabCount
        global tabList
        global tabRows

        self.clearingTabs = True
        for i in range(len(tabList)-1, -1, -1):
            tabList[i].setParent(None) 
            tabList[i].deleteLater()

            # REMOVE ENTRY FROM SAVED TABS FILE
            fileData = []
            with open('tabs.txt', 'r') as inp:
                fileData = inp.readlines()

            with open('tabs.txt', 'w') as out:
                for line in fileData:
                    # CURRENT ITEMS LAYOUT -> (URL IMAGE_PATH TAB_NUMBER)
                    currentItems = line.split(' ')
                    try: 
                        os.remove(os.path.join(IMAGE_FOLDER_PATH, currentItems[1]))
                    except FileNotFoundError:
                        print('File Not Found:::'+str(currentItems[1]))

            tabList.remove(tabList[i])
        os.remove(os.path.join(os.getcwd(), 'tabs.txt'))
        tabCount = 0

        # REMOVE ALL ROWS FROM LIST EXCEPT FIRST AND CLEAR TABS
        for x in range(len(tabRows)-1, -1, -1):
            if tabRows[x].count() > 0:
                tabRows[x].itemAt(0).widget().deleteLater()
            if x == 0:
                tabRows[x].destroyed.connect(lambda: self.newTab(False))
            tabRows[x].deleteLater()
            tabRows.remove(tabRows[x])
        
        self.clearingTabs = False
    
    def close(self):
        self.driver.quit()
        sys.exit(0)