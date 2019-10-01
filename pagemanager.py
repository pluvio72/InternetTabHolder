from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time
from dropsitewindow import DropSiteWindow

class PageManager(QWidget):
    def __init__(self):
        super().__init__()

        self.tabPages = []
        self.openTabPage = DropSiteWindow(1)
        self.tabPages.append(self.openTabPage)
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.openTabPage)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
    
    def newPage(self):
        self.openTabPage.setParent(None)
        newPage = DropSiteWindow(len(self.tabPages)+1)
        self.mainLayout.addWidget(newPage)
        self.openTabPage = newPage
        self.tabPages.append(self.openTabPage)