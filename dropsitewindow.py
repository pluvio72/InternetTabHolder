import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QColor, QIcon
import constants
from droparea import DropArea
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class DropSiteWindow(QWidget):
    def __init__(self):
        super().__init__()

        ###
        ### CHECK ARCHIVED TAB FILE SIZE
        ### ADD SUPPORT FOR MULTIPLE PAGES OF TABS AND NAME THEM??
        ### QUICK START IN OPTIONS OR CHANGE OPTIONS TO FILE MENU
        ### ADD OPTIONS TO CHANGE TABS PER ROW
        ### DONT DELETE PREVIOUSLY DELETED TABS KEEP IMAGE FILE IN _NAME AND _TABLIST CAN BE SHOWN IN MANUAL TAB ADD DIALOG
        ### RETHINK WHETHER YOU HAVE EMPTY TAB AS DROP AREA OR WHOLE WINDOW AS DROP AREA
        ### FAVOURITE TABS HIGHER
        ### SUPPORT MULTIPLE OTHER DATA TYPES E.G. PDF OPENS IN PDF VIEWER
        ### REORDER TABS VERTICALLY????
        ### MAYBE RUN CHECK WITH OS.POPEN IF CHROMEDRIVER INSTANCES ARE MORE THEN 5 OR SO AND KILL THEM
        ### MAKE WINDOW DIALOG SEPARATE CLASS
        ### MAKE CUSTOM WIDGET FOR CLOSE BUTTON
        ### AFTER DELETING TAB TAB COUNT IS TWO WHEN ADDING IT BECOMES TAB AFTER EMPTY TAB SO I NEED TO RETHINK THE LOGIC
        ### ADD SUPPORT FOR DIFFERENT PAGES OF TABS AND RENAMING THEM
        ### IT MAY BE POSSIBLE TO REORGANIZE TAB NUMBERS WHEN DELETING THEM WHEN WRITING DELETED TAB OUT OF FILE
        ### LOOK AT THREADING DRIVER
        ### HANDLE EXCEPTIONS WERE PAGES ARE BLOCKED OR NETWORK DOESNT WORK ETC
        ### WHEN GOING BACK ONLINE LOAD IMAGE??
        ###
        ### CHECKDUPLICATETAB CAN JUST USE CONSTANTS.TABLIST
        ### MAKE STACK OVERFLOW POST ABOUT MAKING THE SET AND CHECK DUPLICATE TAB METHODS MORE GENERIC
        ### REIMPLEMENT LOAD FUNCTION TO MAKE A MIX OF CHECK AND SET DUPLICATE TABS ETC.
        ### DELETE ARCHIVED TAB FROM FILE WHEN READDING
        ###

        # SETUP THUMBNAIL FOLDER 
        if not (os.path.isdir(constants.ABSOLUTE_IMAGE_FOLDER_PATH)): os.mkdir(constants.ABSOLUTE_IMAGE_FOLDER_PATH)

        self.clearingTabs = False
        self.acceptDrops = True

        # SETUP HEADLESS CHROME DRIVER -> SETS IMAGE RESOLUTION (BROWSER_SIZE)
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options, executable_path='./chromedriver_77')
        self.driver.set_window_size(constants.IMAGE_WIDTH, constants.IMAGE_HEIGHT)

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
        self.tabFilePath = os.path.join(os.getcwd(), 'tabs.txt')
        exists = os.path.isfile(self.tabFilePath)
        size = 0
        if exists: size = os.path.getsize(self.tabFilePath)
        if size > 0 and exists:
            self.loadTabs(self.tabFilePath)
        else: self.newTab()
    
    def loadTabs(self, path):
        with open(path, 'r') as f:
            data = f.readlines()
            for index, line in enumerate(data):
                l = line.split('\n')[0]
                currentItems = l.split(' ')
                url = currentItems[0]
                imagePath = currentItems[1]
                tabNumber = currentItems[2]

                tab = self.newTab()
                self.loadTabData(tab, url, imagePath)
                # IF ITS LAST TAB ADD EMPTY TAB AFTER
                if index == len(data)-1:
                    self.newTab()

    def newTab(self):
        if (constants.tabCount % constants.tabsPerRow) == 0:
            self.currentRow = QHBoxLayout()
            self.currentRow.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.currentRow.setSpacing(3)
            self.currentRow.setSizeConstraint(QLayout.SetMinimumSize)
            self.scrollWidgetLayout.insertLayout(self.scrollWidgetLayout.layout().count(), self.currentRow)
            constants.tabRows.append(self.currentRow)

        constants.tabCount += 1
        drp = DropArea(constants.tabCount, self.driver, constants.MIN_TAB_WIDTH, constants.MIN_TAB_HEIGHT, constants.ASPECT_RATIO, constants.ABSOLUTE_IMAGE_FOLDER_PATH)
        drp.imageLoaded.connect(self.newTab)
        drp.tabDeleted.connect(lambda: self.deleteTab(drp))
        drp.tabAdded.connect(self.addTabToList)
        drp.tabReordered.connect(self.reorderTab)
        drp.destroyed.connect(self.reorganizeTabFile)
        constants.emptyTab = drp
        self.currentRow.addWidget(drp)
        return drp
    
    def loadTabData(self, tab, url, imagePath):
        tab.load(url, imagePath)
        
    def deleteTab(self, tab):
        if tab.taken:
            constants.tabCount -= 1
            constants.loadedTabCount -= 1
            constants.tabList.remove(tab)
            tab.setParent(None) 
            tab.deleteLater()

            # REMOVE ENTRY FROM SAVED TABS FILE
            fileData = []
            with open('tabs.txt', 'r') as inp:
                fileData = inp.readlines()

            with open('tabs.txt', 'w') as out:
                # FILE LAYOUT EACH LINE -> (URL IMAGE_PATH TAB_NUMBER)
                for line in fileData:
                    currentItems = line.split(' ')
                    tabNum = int(currentItems[2])
                    # IF CURRENT LINE IS NOT TAB TO BE DELETED WRITE LINE
                    if not (tabNum == tab.tabNumber): out.write(line)
            
            # CHECK IF THERE IS DUPLICATE TAB IF SO DON'T ARCHIVE
            dontArchiveImage = tab.checkDuplicateTab(tab.url, 'tabs.txt')
            if not dontArchiveImage: self.archiveTab(tab.url, tab.imagePath)

    def addTabToList(self, tab, tabNum):
        if len(constants.tabList) <= tabNum: constants.tabList.append(tab)
        else: constants.tabList[tabNum] = tab
    
    def reorderTab(self, tab, swapValue):
        # GET INDEX OF TAB IN TAB LIST
        index = constants.tabList.index(tab)
        # SWAP VALUE = SHIFT IN TABS E.G. -1 FOR ONE LEFT
        newIndex = index + swapValue
        constants.tabList.remove(tab)
        constants.tabList.insert(newIndex, tab)
        self.reorganizeTabFile()

    def reorganizeTabFile(self):
        if os.path.isfile(self.tabFilePath) and os.path.getsize(self.tabFilePath) > 0:
            if not self.clearingTabs:
                for index, tab in enumerate(constants.tabList):
                    tab.tabNumber = index+1
                constants.emptyTab.tabNumber = len(constants.tabList)+1

                # REORDER TABS IN THE SAVED TABS FILE SO THEY HAVE CORRECT TAB NUMBER
                with open('tabs.txt', 'r+') as f:
                    lines = f.readlines()
                    currentTab = 1
                    finalStringData = ''
                    for line in lines:
                        currentItems = line.split('\n')[0].split(' ')
                        # REORGANIZING AFTER DELETING A TAB
                        if(currentTab != int(currentItems[2])): finalStringData += currentItems[0] + ' ' + constants.tabList[currentTab-1].imagePath + ' ' + str(currentTab) + '\n'
                        # REORGANIZING AFTER REORDERING A TAB
                        elif(currentItems[0] != constants.tabList[currentTab-1].url):
                            current = constants.tabList[currentTab-1]
                            finalStringData += current.url + ' ' + current.imagePath + ' ' + str(current.tabNumber) + '\n'
                        else: finalStringData += line
                        currentTab += 1

                    # SEEK BEGINNING -> CLEAR FILE -> WRITE DATA (TRUNCATE SETS FILE SIZE TO MAX (0))
                    f.seek(0)
                    f.truncate(0)
                    f.write(finalStringData)
        self.checkLayouts()
    
    def checkLayouts(self):
        #IF ANY LAYOUTS HAVE < 3 CHILDREN REORGANIZE THE WIDGETS
        complete = False
        while not complete:
            for i in range(0, len(constants.tabRows)-1):
                if constants.tabRows[i].count() < 3:
                    child = constants.tabRows[i + 1].itemAt(0)
                    constants.tabRows[i + 1].removeItem(child)
                    constants.tabRows[i].addItem(child)
            complete = True
                
        # IF CURRENT ROW HAS NO CHILDREN REMOVE IT AND SET IT TO PREVIOUS ROW
        if self.currentRow.count() == 0:
            constants.tabRows.remove(self.currentRow)
            self.currentRow.deleteLater()
            self.currentRow = constants.tabRows[len(constants.tabRows)-1]

    def clear(self):
        self.clearingTabs = True
        for i in range(len(constants.tabList)-1, -1, -1):
            constants.tabList[i].setParent(None) 
            constants.tabList[i].deleteLater()

            # REMOVE ENTRY FROM SAVED TABS FILE
            fileData = ''
            with open('tabs.txt', 'r') as inp:
                fileData += inp.readlines()

            with open('tabs.txt', 'w') as out:
                for line in fileData:
                    currentItems = line.split(' ')
                    self.archiveTab(currentItems[0], currentItems[1])
            constants.tabList.remove(constants.tabList[i])
        os.remove(self.tabFilePath)
        constants.tabCount = 0

        # REMOVE ALL ROWS FROM LIST EXCEPT FIRST AND CLEAR TABS
        for x in range(len(constants.tabRows)-1, -1, -1):
            if constants.tabRows[x].count() > 0: constants.tabRows[x].itemAt(0).widget().deleteLater()
            if x == 0: constants.tabRows[x].destroyed.connect(self.newTab)
            constants.tabRows[x].deleteLater()
            constants.tabRows.remove(constants.tabRows[x])
        self.clearingTabs = False
    
    def archiveTab(self, url, imagePath):
        try: os.rename(os.path.join(constants.IMAGE_FOLDER_PATH, imagePath), os.path.join(constants.IMAGE_FOLDER_PATH, '.'+imagePath))
        except FileNotFoundError: print('RENAMING:::File Not Found:::' + imagePath)

        with open('.tabs.txt', 'a+') as f:
            f.seek(0)
            lines = f.readlines()
            duplicate = False
            for line in lines:
                if line.split(' ')[0] == url:
                    duplicate = True
            if not duplicate: f.write(url + ' ' + '.' + imagePath + '\n')
    
    def close(self):
        self.driver.quit()
        print('Exited')
        sys.exit(0)