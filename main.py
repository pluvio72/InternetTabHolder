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

ASPECT_RATIO = (float)(1080/1920)

MIN_TAB_WIDTH = 360
MIN_TAB_HEIGHT = (int)(MIN_TAB_WIDTH*ASPECT_RATIO)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        ###
        ### CHANGE TABS PER ROW ON RESIZE???
        ### INSTEAD OF + 100 IN THE SETMINSIZE TRY TO FIND CONTENT MARGIN
        ### SET DROP AREA IMAGE PATH SO IT CAN BE ACCESSED WHEN RESIZING OR RELOADING ETC.
        ### FAVOURITE TABS HIGHER
        #### SUPPORT MULTIPLE OTHER DATA TYPES E.G. PDF OPENS IN PDF VIEWER
        ### REORDER TABS
        ###

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

        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.scroll.setWidget(self.scrollWidget)
        self.mainLayout.addWidget(self.scroll)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)

        self.setMouseTracking(True)
        self.setWindowTitle("Tab Holder")
        self.setMinimumSize(MIN_TAB_WIDTH*3 + 100, MIN_TAB_HEIGHT*3)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

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
            self.currentRow.setAlignment(Qt.AlignTop)
            self.currentRow.setSpacing(5)
            self.scrollWidgetLayout.insertLayout(self.scrollWidgetLayout.layout().count(), self.currentRow)
            self.tabRows.append(self.currentRow)

        self.tabCount += 1
        drp = DropArea(self.tabCount, self.driver, MIN_TAB_WIDTH, MIN_TAB_HEIGHT, ASPECT_RATIO)
        drp.imageLoaded.connect(self.newTab)
        drp.tabDeleted.connect(lambda: self.deleteTab(drp))
        drp.tabAdded.connect(self.addTabToList)
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
                else: os.remove(os.path.join(os.getcwd(), currentItems[1]))

    def addTabToList(self, tab, tabNo):
        if len(self.tabList) <= tabNo:
            self.tabList.append(tab)
        else:
            self.tabList[tabNo] = tab

    def reorganizeTabList(self):
        for index, tab in enumerate(self.tabList):
            tab.tabNumber = index
            tab.imagePath = str(index) + '.png'

        #REORDER TABS IN THE SAVED TABS FILE SO THEY HAVE CORRECT TAB NUMBER
        with open('tabs.txt', 'r+') as f:
            lines = f.readlines()
            currentTab = 1
            finalStringData = ''
            for line in lines:
                l = line.split('\n')[0]
                currentItems = l.split(' ')
                currentString = ''
                if(currentTab != int(currentItems[2])):
                    currentString += currentItems[0] + ' ' + str(currentTab) + '.png ' + str(currentTab) + '\n'
                    os.rename(os.path.join(os.getcwd(), currentItems[1]), os.path.join(os.getcwd(), str(currentTab) + '.png'))
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
        #for i in range(len(self.tabList)-1, -1):
        #    self.tabList.remove(i)
        #    self.tabList[i].setParent(None)
        #    self.tabList[i].deleteLater()
        
        #for i in range(len(self.tabRows)-1, -1):
        #    self.tabRows.remove(i)
        
        for tab in self.tabList:
            self.deleteTab(tab)

        #while not (self.scrollWidgetLayout.isEmpty()):
        #    currentLayout = self.scrollWidgetLayout.itemAt(0).layout()
        #    while not (currentLayout.isEmpty()):
        #        currentWidget = currentLayout.itemAt(0).widget()
        #        currentLayout.
    
    def quit(self):
        self.driver.quit()
        sys.exit(0)
        print('Exiting')

if __name__ == '__main__':
    app = QApplication([])

    widget = MainWindow()
    widget.resize(800, 600)
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
