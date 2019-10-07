import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QColor, QIcon
from droparea import DropArea
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tabsettings

class DropSiteWindow(QWidget):
    def __init__(self, pageNumber, driver):
        super().__init__()

        """
            LOOK AT THREADING DRIVER
            QUICK START IN OPTIONS
            HANDLE EXCEPTIONS WERES ARE BLOCKED OR NETWORK DOESNT WORK ETC -> WHEN GOING BACK ONLINE LOAD IMAGE
            REIMPLEMENT LOAD FUNCTION TO MAKE A MIX OF CHECK AND SET DUPLICATE TABS ETC.
            WINDOW DOESN'T SHOW IN APPLE MISSION CONTROL -> MAYBE SOMETHING TO DO WITH WINDOW MODALITY
            COMMENT EVERYTHING BEFORE I BUILD


            ONLY IMPORT NEEDED CLASSES


            FUTURE FEATURES:
             - MORE FREEDOM WITH REARRANGING TABS
             - SUPPORT OTHER DATA TYPES E.G. PDF FILE ETC..
             - FAVOURITE TABS -> MOVES THEM HIGHER
             - ANIMATE CLOSE BUTTON FADE IN/OUT
             - IMPLEMENT THEMES (ONLY DARK MODE RIGHT NOW)
        """   

        # SETUP THUMBNAIL FOLDER 
        if not (os.path.isdir(tabsettings.absImageFolderPath())): os.mkdir(tabsettings.absImageFolderPath())

        self.clearingTabs = False
        self.acceptDrops = True
        self.options = tabsettings.TabSettings()
        self.pageNumber = pageNumber
        self.pageName = 'Page ' + str(self.pageNumber)
        self.driver = driver

        self.setPageName()

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
        self.tabFilePath = os.path.join(os.getcwd(), tabsettings.tabFileName(self))
        self.tabFileName = tabsettings.tabFileName(self)
        self.archiveTabFileName = tabsettings.archiveTabFileName(self)
        exists = os.path.isfile(self.tabFilePath)
        size = 0
        if exists: size = os.path.getsize(self.tabFilePath)
        if size > 0 and exists:
            self.loadTabs(self.tabFilePath)
        else: self.newTab()

        self.updatePageNames()
        self.checkArchiveTabFileSize()
    
    # LOAD TABS FROM CURRENT PAGE TAB FILE -> CREATE NEW TAB -> LOAD TAB WITH CONTENT OF TAB FILE ENTRY
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

    # CREATE NEW TAB -> IF TABCOUNT > ALLOWED -> CREATE NEW ROW THEN ADD TAB
    def newTab(self):
        if (self.options.tabCount % self.options.tabsPerRow) == 0:
            self.currentRow = QHBoxLayout()
            self.currentRow.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.currentRow.setSpacing(3)
            self.currentRow.setSizeConstraint(QLayout.SetMinimumSize)
            self.scrollWidgetLayout.insertLayout(self.scrollWidgetLayout.layout().count(), self.currentRow)
            self.options.tabRows.append(self.currentRow)

        self.options.tabCount += 1
        drp = DropArea(self.options, self.options.tabCount, self.driver, 
        tabsettings.MIN_TAB_WIDTH, tabsettings.MIN_TAB_HEIGHT, tabsettings.ASPECT_RATIO, 
        tabsettings.absImageFolderPath(), self.tabFileName, self.archiveTabFileName)
        drp.imageLoaded.connect(self.newTab)
        drp.tabDeleted.connect(lambda: self.deleteTab(drp))
        drp.tabAdded.connect(self.addTabToList)
        drp.tabReordered.connect(self.reorderTab)
        drp.destroyed.connect(self.reorganizeTabFile)
        self.options.emptyTab = drp
        self.currentRow.addWidget(drp)
        return drp
    
    # SHORTCUT METHOD TO LOAD TAB 
    def loadTabData(self, tab, url, imagePath):
        tab.load(url, imagePath)
        
    # DELETE TAB -> SET PARENT NONE -> REMOVE FROM TAB LIST -> DELETE ENTRY IN TAB FILE -> ARCHIVE IF NOT DUPLICATE
    def deleteTab(self, tab):
        if tab.taken:
            self.options.tabCount -= 1
            self.options.loadedTabCount -= 1
            self.options.tabList.remove(tab)
            tab.setParent(None) 
            tab.deleteLater()

            # REMOVE ENTRY FROM SAVED TABS FILE
            fileData = open(self.tabFileName, 'r').readlines()
            with open(self.tabFileName, 'w') as out:
                # FILE LAYOUT EACH LINE -> (URL IMAGE_PATH TAB_NUMBER)
                for line in fileData:
                    currentItems = line.split(' ')
                    tabNum = int(currentItems[2])
                    # IF CURRENT LINE IS NOT TAB TO BE DELETED WRITE LINE
                    if not (tabNum == tab.tabNumber): out.write(line)
            
            # CHECK IF THERE IS DUPLICATE TAB IF SO DON'T ARCHIVE
            dontArchiveImage = tab.checkDuplicateTab(tab.url, self.tabFileName)
            if not dontArchiveImage: self.archiveTab(tab.url, tab.imagePath)

    # ARCHIVE TAB IN ARCHIVE TAB FILE NAME OF CURRENT PAGE -> RENAME IMAGE TO .IMAGE IF ITS AVAILABLE
    def archiveTab(self, url, imagePath):
        try: os.rename(os.path.join(tabsettings.IMAGE_FOLDER_PATH, imagePath), os.path.join(tabsettings.IMAGE_FOLDER_PATH, '.'+imagePath))
        except FileNotFoundError: pass

        with open(self.archiveTabFileName, 'a+') as f:
            f.seek(0)
            lines = f.readlines()
            duplicate = False
            for line in lines:
                if line.split(' ')[0] == url:
                    duplicate = True
            if not duplicate: f.write(url + ' ' + '.' + imagePath + '\n')

    # ADD TAB TO TABLIST -> IF NUMBER GREATER THEN LIST SIZE -> APPEND -> ELSE REPLACE TAB IN LIST
    def addTabToList(self, tab, tabNum):
        if len(self.options.tabList) <= tabNum: self.options.tabList.append(tab)
        else: self.options.tabList[tabNum] = tab

    # REORDER TAB IN TABLIST AND MOVE WIDGET -> REORGANIZE TAB FILE TO SHOW CHANGES MADE
    def reorderTab(self, tab, swapValue):
        # GET INDEX OF TAB IN TAB LIST
        index = self.options.tabList.index(tab)
        # SWAP VALUE = SHIFT IN TABS E.G. -1 FOR ONE LEFT
        newIndex = index + swapValue
        self.options.tabList.remove(tab)
        self.options.tabList.insert(newIndex, tab)
        self.reorganizeTabFile()

    # REORGANIZE TAB FILE -> FROM DELETED TAB (TAB NUMBERS WRONG) -> OR FROM REORGANIZING TAB
    def reorganizeTabFile(self):
        if os.path.isfile(self.tabFilePath) and os.path.getsize(self.tabFilePath) > 0:
            if not self.clearingTabs:
                for index, tab in enumerate(self.options.tabList):
                    tab.tabNumber = index+1
                self.options.emptyTab.tabNumber = len(self.options.tabList)+1

                # REORDER TABS IN THE SAVED TABS FILE SO THEY HAVE CORRECT TAB NUMBER
                with open(self.tabFileName, 'r+') as f:
                    lines = f.readlines()
                    currentTab = 1
                    finalStringData = ''
                    for line in lines:
                        currentItems = line.split('\n')[0].split(' ')
                        # REORGANIZING AFTER DELETING A TAB
                        if(currentTab != int(currentItems[2])): finalStringData += currentItems[0] + ' ' + self.options.tabList[currentTab-1].imagePath + ' ' + str(currentTab) + '\n'
                        # REORGANIZING AFTER REORDERING A TAB
                        elif(currentItems[0] != self.options.tabList[currentTab-1].url):
                            current = self.options.tabList[currentTab-1]
                            finalStringData += current.url + ' ' + current.imagePath + ' ' + str(current.tabNumber) + '\n'
                        else: finalStringData += line
                        currentTab += 1

                    # SEEK BEGINNING -> CLEAR FILE -> WRITE DATA (TRUNCATE SETS FILE SIZE TO MAX (0))
                    f.seek(0)
                    f.truncate(0)
                    f.write(finalStringData)
        self.checkLayouts()
    
    # CHECK IF ANY LAYOUTS HAVE < 3 CHILDREN APART FROM LAST -> MOVE WIDGETS TO PREVIOUS LAYOUT/ROW ::: IF CURRENT ROW EMPTY -> SET TO PREVIOUS ROW
    def checkLayouts(self):
        # IF ANY LAYOUTS HAVE < 3 CHILDREN REORGANIZE THE WIDGETS
        complete = False
        while not complete:
            for i in range(0, len(self.options.tabRows)-1):
                if self.options.tabRows[i].count() < 3:
                    child = self.options.tabRows[i + 1].itemAt(0)
                    self.options.tabRows[i + 1].removeItem(child)
                    self.options.tabRows[i].addItem(child)
            complete = True
                
        # IF CURRENT ROW HAS NO CHILDREN REMOVE IT AND SET IT TO PREVIOUS ROW
        if self.currentRow.count() == 0:
            self.options.tabRows.remove(self.currentRow)
            self.currentRow.deleteLater()
            self.currentRow = self.options.tabRows[len(self.options.tabRows)-1]

    # CLEAR ALL TABS IN CURRENT PAGE -> EMPTY TABLIST AND TABROWS -> ARCHIVE ALL DELETED TABS
    def clear(self):
        self.clearingTabs = True

        # REMOVE ENTRY FROM SAVED TABS FILE
        fileData = []
        with open(self.tabFileName, 'r') as inp:
            fileData += inp.readlines()

        for line in fileData:
            currentItems = line.split(' ')
            self.archiveTab(currentItems[0], currentItems[1])

        for i in range(len(self.options.tabList)-1, -1, -1):
            self.options.tabList[i].setParent(None) 
            self.options.tabList[i].deleteLater()
            self.options.tabList.remove(self.options.tabList[i])
        os.remove(self.tabFilePath)
        self.options.tabCount = 0

        # REMOVE ALL ROWS FROM LIST EXCEPT FIRST AND CLEAR TABS
        for x in range(len(self.options.tabRows)-1, -1, -1):
            if self.options.tabRows[x].count() > 0: self.options.tabRows[x].itemAt(0).widget().deleteLater()
            if x == 0: self.options.tabRows[x].destroyed.connect(self.newTab)
            self.options.tabRows[x].deleteLater()
            self.options.tabRows.remove(self.options.tabRows[x])
        self.clearingTabs = False
    
    # CLEARS ALL TABS BUT DOES NOT REMOVE THEM OR ARCHIVE THEM AND RESETS VARIABLES
    def cleanClear(self):
        for i in reversed(range(len(self.options.tabRows))):
            for j in reversed(range(self.options.tabRows[i].count())):
                self.options.tabRows[i].itemAt(j).widget().setParent(None)
        
        self.options.tabRows.clear()
        self.options.tabList.clear()
        self.options.emptyTab = None
        self.options.tabCount = 0
        self.options.loadedTabCount = 0

    # RUN AFTER CLEAN CLEAR JUST RELOADS ALL TABS INTO WINDOW
    def cleanLoad(self):
        with open(self.tabFileName, 'r') as f:
            for line in f:
                current = line.split('\n')[0].split(' ')
                url = current[0]
                imagePath = current[1]
                tabNumber = current[2]
                drp = self.newTab()
                drp.load(url, imagePath)
        self.newTab()
                
    # CHANGE TABS PER ROW IN CURRENT PAGE OPTIONS -> CHANGE MIN WIDTH/HEIGHT -> RELOAD ALL TABS
    def changeTabsPerRow(self, number):
        self.clearingTabs = True
        tabsettings.MIN_TAB_WIDTH *= (self.options.tabsPerRow/number)
        tabsettings.MIN_TAB_HEIGHT *= (self.options.tabsPerRow/number)
        self.options.tabsPerRow = number
        self.cleanClear()
        self.cleanLoad()
        self.clearingTabs = False

    # SET PAGE NAME FROM ENTRY IN PAGENAMES.TXT BY PAGENUMBER
    def setPageName(self):
        if os.path.exists(os.path.join(os.getcwd(), 'pagenames.txt')): 
            with open('pagenames.txt', 'r+') as f:
                for index, line in enumerate(f.readlines()):
                    if index+1 == self.pageNumber:
                        self.pageName = line.split('\n')[0]

    # UPDATE PAGENAMES.TXT -> IF DOESN'T EXIST -> WRITE PAGENAME -> ELSE REWRITE ENTRY TO PAGENAME -> OR IF NEW PAGE WRITE NEW LINE
    def updatePageNames(self):
        if not os.path.exists(os.path.join(os.getcwd(), 'pagenames.txt')):
            with open('pagenames.txt', 'a+') as f:
                f.write(self.pageName + '\n')
        else:
            data = open('pagenames.txt', 'r').readlines()
            # IF NUMBER OF LINES >= NUMBER THEN NAME WILL BE IN FILE
            if len(data) >= self.pageNumber:
                with open('pagenames.txt', 'w') as f:
                    for index, line in enumerate(data):
                        if index+1 == self.pageNumber:
                            f.write(self.pageName + '\n')
                        else:
                            f.write(line)
            # NAME IS NOT IN FILE SO MUST APPEND IT TO FILE
            else:
                with open('pagenames.txt', 'a') as f:
                    f.write(self.pageName + '\n')

    # SET PAGENAME AND UPDATE PAGENAMES.TXT WITH NEW NAME
    def rename(self, string):
        self.pageName = string
        self.updatePageNames()

    # CHECK IF ARCHIVE TAB FILE SIZE IS GREATER THEN VALUE -> REWRITE OUT FIRST LINES UNTIL ITS DESIRED SIZE
    def checkArchiveTabFileSize(self):
        if os.path.isfile(os.path.join(os.getcwd(), self.archiveTabFileName)):
            data = open(self.archiveTabFileName, 'r').readlines()
            if len(data) > tabsettings.ARCHIVE_TAB_FILE_MAX_SIZE:
                with open(self.archiveTabFileName, 'w') as f:
                    for index, line in enumerate(data):
                        if index != 0 and index <= tabsettings.ARCHIVE_TAB_FILE_MAX_SIZE:
                            f.write(line)


    #####
    ####
    def writeLog(self, text):
        with open('/Users/maksie/Documents/Coding/Python/Projects/PyChromeTabs/mylog.txt', 'a') as f:
            f.write(text)
    #####
    ######

    
    def close(self):
        self.driver.close()
        self.driver.quit()
        print('Exited')
        sys.exit(0)