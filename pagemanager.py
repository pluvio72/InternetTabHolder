from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from dropsitewindow import DropSiteWindow
from tabsettings import IMAGE_WIDTH, IMAGE_HEIGHT
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sys import platform, exit
import os

class PageManager(QWidget):
    changeWindowTitle = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        options = Options()
        options.headless = True

        driver_path = os.environ['chrome_driver']
        self.writeLog(driver_path)

        self.driver = webdriver.Chrome(options=options, executable_path=driver_path)
        self.driver.set_window_size(IMAGE_WIDTH, IMAGE_HEIGHT)

        self.tabPages = []
        self.loadPages()

        self.openTabPage = DropSiteWindow(1, self.driver)
        self.tabPages.append(self.openTabPage)
        self.currentPage = 1

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.openTabPage)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
    
    # LOAD PAGES INTO TABPAGES ARRAY SO WHEN ACCESSING NEXT PAGE ELEMENT IS THERE
    def loadPages(self):
        if os.path.isfile(os.path.join(os.getcwd(), 'pagenames.txt')):
            data = open('pagenames.txt', 'r').readlines()
            for index, page in enumerate(data):
                self.tabPages.append(DropSiteWindow(index+1, self.driver))

    # CMD+N -> DELETES OLD PAGE -> CREATES NEW PAGE -> SETS PARENT TO THIS -> UPDATES WINDOW TITLE + CURRENT PAGE
    def newPage(self):
        self.currentPage += 1
        self.openTabPage.setParent(None)
        newPage = DropSiteWindow(self.currentPage, self.driver)
        self.mainLayout.addWidget(newPage)
        self.openTabPage = newPage
        self.tabPages.append(self.openTabPage)
        self.changeWindowTitle.emit(self.openTabPage.pageName)
    
    def setPage(self, page):
        self.mainLayout.addWidget(page)
        self.openTabPage = page
        self.changeWindowTitle.emit(self.openTabPage.pageName)
    
    # CMD+RIGHT IF CURRENT PAGE ISN'T LAST -> LOAD PAGE --> ELSE DON'T DO ANYTHING
    def nextPage(self):
        if self.currentPage < len(self.tabPages):
            self.currentPage += 1
            self.openTabPage.setParent(None)
            page = DropSiteWindow(self.currentPage, self.driver)
            self.setPage(page)
    
    # CMD+LEFT SAME AS BOVE BUT PREVIOUS PAGE
    def prevPage(self):
        if self.currentPage > 1:
            self.currentPage -= 1
            self.openTabPage.setParent(None)
            page = DropSiteWindow(self.currentPage, self.driver)
            self.setPage(page)
    
    # CMD+R -> UPDATES WINDOW TITLE -> RENAMES PAGE NAME IN PAGENAMES.TXT
    def renamePage(self, string):
        self.openTabPage.rename(string)
        self.changeWindowTitle.emit(self.openTabPage.pageName)
    
    # SEND UPDATE TITLE SIGNAL TO PARENT WINDOW
    def updateTitle(self):
        self.changeWindowTitle.emit(self.openTabPage.pageName)

    


    def writeLog(self, text):
        with open('mylog.txt', 'a') as f:
            f.write(text)