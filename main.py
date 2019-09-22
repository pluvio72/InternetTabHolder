import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QColor, QIcon
from droparea import DropArea
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
ASPECT_RATIO = (float)(IMAGE_HEIGHT/IMAGE_WIDTH)
MIN_TAB_WIDTH = 360
MIN_TAB_HEIGHT = (int)(MIN_TAB_WIDTH*ASPECT_RATIO)

ABSOLUTE_IMAGE_FOLDER_PATH = os.path.join(os.getcwd(), 'thumbnails')
IMAGE_FOLDER_PATH = 'thumbnails'

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        ###
        ### MAKE CHECK WHEN REORDERING TABS IF ITS FIRST ELEMENT IN ROW
        ### RETHINK WHETHER YOU HAVE EMPTY TAB AS DROP AREA OR WHOLE WINDOW AS DROP AREA
        ### MAKE FILE WITH CONSTANTS???
        ### WHEN DELETING TAB RENAME THE IMAGE FOR IT AS THE URL IN CASE TO OPEN AGAIN
        #### WHEN CLICKING EMPTY TAB SHOW PREVIOUSLY DELETED IN DIALOG
        ### AFTER FIRST FULL ROW DONT LET THE NEW TAB SPAN WHOLE ROW
        ### FIX SPACING BETWEEN ROWS WHEN GETTING SMALLER WINDOW
        ### CHANGE TABS PER ROW ON RESIZE???
        ### INSTEAD OF + 100 IN THE SETMINSIZE TRY TO FIND CONTENT MARGIN
        ### SET DROP AREA IMAGE PATH SO IT CAN BE ACCESSED WHEN RESIZING OR RELOADING ETC.
        ### FAVOURITE TABS HIGHER
        #### SUPPORT MULTIPLE OTHER DATA TYPES E.G. PDF OPENS IN PDF VIEWER
        ### REORDER TABS VERTICALLY????
        ### DONT HARDCODE WINDOW SIZE
        ###

        #SETUP THUMBNAIL FOLDER 
        if not (os.path.isdir(ABSOLUTE_IMAGE_FOLDER_PATH)): os.mkdir(ABSOLUTE_IMAGE_FOLDER_PATH)

        self.tabCount = 0
        self.tabRows = []
        self.tabList = []

        # SETUP HEADLESS CHROME DRIVER -> SETS IMAGE RESOLUTION (BROWSER_SIZE)
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options, executable_path='./chromedriver')
        self.driver.set_window_size(IMAGE_WIDTH, IMAGE_HEIGHT)

        # SETUP BUTTON BOX AND SIGNALS/SLOTS
        clearButton = QPushButton('Clear')
        quitButton = QPushButton('Quit')
        clearButton.clicked.connect(self.clearTabs)
        quitButton.clicked.connect(self.quit)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton(clearButton, QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(quitButton, QDialogButtonBox.RejectRole)

        # SETUP LAYOUTS
        self.mainLayout = QVBoxLayout()
        self.scroll = QScrollArea()
        self.scrollWidget = QWidget()
        self.scrollWidgetLayout = QVBoxLayout()
        
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setFrameStyle(QFrame.NoFrame)

        self.scrollWidgetLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scrollWidgetLayout.setSpacing(3)

        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollWidgetLayout.setContentsMargins(0, 6, 0, 0)

        print('Main Layout Margins: ', self.mainLayout.getContentsMargins())
        print('Scroll Margins: ', self.scroll.getContentsMargins())
        print('Scroll Widget Margins: ', self.scrollWidget.getContentsMargins())
        print('Scroll Widget Layout Margins: ', self.scrollWidgetLayout.getContentsMargins())

        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.scroll.setWidget(self.scrollWidget)
        self.mainLayout.addWidget(self.scroll)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)

        self.setMouseTracking(True)
        self.setWindowTitle("Internet Tab Holder")
        self.setMinimumSize(MIN_TAB_WIDTH*3 + 100, MIN_TAB_HEIGHT*3)

        #self.setWindowFlags(Qt.WindowStaysOnTopHint)

        #IF TAB FILE EXISTS REMAKE TABS
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

                if index == len(data)-1:
                    self.newTab(True, url, imagePath, True)
                else:
                    self.newTab(True, url, imagePath, False)

    def newTab(self, new, url=None, imagePath=None, addTabAfter=False):
        if (self.tabCount % 3) == 0:
            self.currentRow = QHBoxLayout()
            self.currentRow.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.currentRow.setSpacing(3)
            self.currentRow.setSizeConstraint(QLayout.SetMinimumSize)
            self.scrollWidgetLayout.insertLayout(self.scrollWidgetLayout.layout().count(), self.currentRow)
            self.tabRows.append(self.currentRow)

        self.tabCount += 1
        drp = DropArea(self.tabCount, self.driver, MIN_TAB_WIDTH, MIN_TAB_HEIGHT, ASPECT_RATIO, ABSOLUTE_IMAGE_FOLDER_PATH)
        drp.imageLoaded.connect(self.newTab)
        drp.tabDeleted.connect(lambda: self.deleteTab(drp))
        drp.tabAdded.connect(self.addTabToList)
        drp.tabReordered.connect(self.reorderTab)
        drp.destroyed.connect(self.reorganizeTabList)
        self.currentRow.addWidget(drp)

        #IF ITS A NEW TAB LOAD IAMGE AND URL
        if new: drp.load(url, imagePath, addTabAfter)

    def deleteTab(self, tab):
        if self.tabCount == 1:
            tab.taken = False
            tab.clear()
        else:
            self.tabCount -= 1
            self.tabList.remove(tab)
            tab.setParent(None) 
            tab.deleteLater()

        # REMOVE ENTRY FROM SAVED TABS FILE
        fileData = []
        with open('tabs.txt', 'r') as inp:
            fileData = inp.readlines()

        with open('tabs.txt', 'w') as out:
            for line in fileData:
                # CURRENT ITEMS LAYOUT -> (URL IMAGE_PATH TAB_NUMBER)
                currentItems = line.split(' ')
                tabNum = int(currentItems[2])
                if not (tabNum == tab.tabNumber): out.write(line)
                else: os.remove(os.path.join(IMAGE_FOLDER_PATH, currentItems[1]))

    def addTabToList(self, tab, tabNo):
        if len(self.tabList) <= tabNo:
            self.tabList.append(tab)
        else:
            self.tabList[tabNo] = tab
    
    def reorderTab(self, tab, swapValue):
        index = self.tabList.index(tab)
        #SWAP VALUE = SHIFT IN TABS E.G. -1 FOR ONE LEFT
        newIndex = index + swapValue
        self.tabList.remove(tab)
        self.tabList.insert(newIndex, tab)

        self.reorganizeTabList()


    def reorganizeTabList(self):
        for index, tab in enumerate(self.tabList):
            #TAB NUMBERS START AT 1
            tab.tabNumber = index+1

        #REORDER TABS IN THE SAVED TABS FILE SO THEY HAVE CORRECT TAB NUMBER
        with open('tabs.txt', 'r+') as f:
            lines = f.readlines()
            currentTab = 1
            finalStringData = ''
            for line in lines:
                l = line.split('\n')[0]
                currentItems = l.split(' ')
                currentString = ''
                #REORGANIZING AFTER DELETING A TAB
                if(currentTab != int(currentItems[2])):
                    currentString += currentItems[0] + ' ' + str(currentTab) + '.png ' + str(currentTab) + '\n'
                    os.rename(os.path.join(IMAGE_FOLDER_PATH, currentItems[1]), os.path.join(IMAGE_FOLDER_PATH, str(currentTab) + '.png'))
                #REORGANIZING AFTER REORDERING A TAB
                elif(currentItems[0] != self.tabList[currentTab-1].url):
                    current = self.tabList[currentTab-1]
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
            for i in range(0, len(self.tabRows)-1):
                if self.tabRows[i].count() < 3:
                    child = self.tabRows[i + 1].itemAt(0)
                    self.tabRows[i + 1].removeItem(child)
                    self.tabRows[i].addItem(child)
            complete = True
        
        #IF CURRENT ROW HAS NO CHILDREN REMOVE IT AND SET IT TO PREVIOUS ROW
        if self.currentRow.count() == 0:
            self.tabRows.remove(self.currentRow)
            self.currentRow.deleteLater()
            self.currentRow = self.tabRows[len(self.tabRows)-1]

    def resizeEvent(self, event):
        pass

    def clearTabs(self):
        for i in range(len(self.tabList)-1, -1, -1):
            self.tabList[i].setParent(None) 
            self.tabList[i].deleteLater()

            # REMOVE ENTRY FROM SAVED TABS FILE
            fileData = []
            with open('tabs.txt', 'r') as inp:
                fileData = inp.readlines()

            with open('tabs.txt', 'w') as out:
                for line in fileData:
                    # CURRENT ITEMS LAYOUT -> (URL IMAGE_PATH TAB_NUMBER)
                    currentItems = line.split(' ')
                    tabNum = int(currentItems[2])
                    if not (tabNum == self.tabList[i].tabNumber): out.write(line)
                    else:
                        try: 
                            os.remove(os.path.join(IMAGE_FOLDER_PATH, currentItems[1]))
                        except FileNotFoundError:
                            print('File Not Found:::'+str(currentItems[1]))

            self.tabList.remove(self.tabList[i])
            self.tabCount = 0
    
    def quit(self):
        self.driver.quit()
        sys.exit(0)

if __name__ == '__main__':
    app = QApplication([])

    widget = MainWindow()
    #widget.resize(800, 600)
    widget.show()

    app.aboutToQuit.connect(widget.quit)
    #app.setStyle('macintosh')

    style = QPalette()
    style.setColor(QPalette.Window, QColor(53, 53, 53))
    style.setColor(QPalette.Background, QColor(53, 53, 53))
    style.setColor(QPalette.WindowText, Qt.red)
    style.setColor(QPalette.Base, QColor(25, 25, 25))
    style.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    style.setColor(QPalette.ToolTipBase, Qt.white)
    style.setColor(QPalette.ToolTipText, Qt.white)
    style.setColor(QPalette.Text, Qt.red)
    style.setColor(QPalette.Button, QColor(53, 53, 53))
    style.setColor(QPalette.ButtonText, QColor(42, 42, 42))
    style.setColor(QPalette.BrightText, Qt.red)
    style.setColor(QPalette.Link, QColor(42, 130, 218))
    style.setColor(QPalette.Highlight, QColor(42, 130, 218))
    style.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(style)

    sys.exit(app.exec_())
