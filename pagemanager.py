from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from dropsitewindow import DropSiteWindow
from tabsettings import IMAGE_WIDTH, IMAGE_HEIGHT
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class PageManager(QWidget):
    changeWindowTitle = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options, executable_path='./chromedriver_77')
        self.driver.set_window_size(IMAGE_WIDTH, IMAGE_HEIGHT)

        self.tabPages = []
        self.openTabPage = DropSiteWindow(1, self.driver)
        self.tabPages.append(self.openTabPage)
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.openTabPage)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
    
    def newPage(self):
        self.openTabPage.setParent(None)
        newPage = DropSiteWindow(len(self.tabPages)+1, self.driver)
        self.mainLayout.addWidget(newPage)
        self.openTabPage = newPage
        self.tabPages.append(self.openTabPage)
        self.changeWindowTitle.emit(self.openTabPage.pageName)
    
    def renamePage(self, string):
        self.openTabPage.pageName = string
        self.openTagPage.rename(string)
        self.changeWindowTitle.emit(self.openTabPage.pageName)