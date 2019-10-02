import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QColor, QIcon
from pagemanager import PageManager
from dropsitewindow import DropSiteWindow
from tabsettings import MIN_TAB_WIDTH, MIN_TAB_HEIGHT, WINDOW_NAME

ABSOLUTE_IMAGE_FOLDER_PATH = os.path.join(os.getcwd(), 'thumbnails')
IMAGE_FOLDER_PATH = 'thumbnails'

class MainWindow(QMainWindow):
    def __init__(self, centralWidget, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setMinimumSize(MIN_TAB_WIDTH*3 + 12, MIN_TAB_HEIGHT*3+14)
        self.setWindowTitle('Internet Tab Holder') 
        self.setCentralWidget(centralWidget)
        self.setMouseTracking(True)

        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.centralWidget = centralWidget
        self.centralWidget.changeWindowTitle.connect(self.changeTitle)
        self.createMenu()

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def createMenu(self):
        menuBar = self.menuBar()
        file = menuBar.addMenu("File")

        newAction = QAction("New Page", self)
        newAction.setShortcut("Ctrl+N")
        newAction.triggered.connect(self.centralWidget.newPage)
        file.addAction(newAction)

        renameAction = QAction("Rename Page", self)
        renameAction.setShortcut("Ctrl+R")
        renameAction.triggered.connect(self.openRenameDialog)
        file.addAction(renameAction)

        clearAction = QAction("Clear Tabs", self)
        clearAction.setShortcut("Ctrl+Shift+W")
        clearAction.triggered.connect(self.centralWidget.openTabPage.clear)
        file.addAction(clearAction)

        self.changeTabMenu = file.addMenu("Tabs Per Row")
        self.tabsPerRowList = []
        a1 = QAction("3 Tabs", self)
        a2 = QAction("4 Tabs", self)
        a3 = QAction("5 Tabs", self)
        a1.setShortcut("Alt+Shift+3")
        a2.setShortcut("Alt+Shift+4")
        a3.setShortcut("Alt+Shift+5")
        self.changeTabMenu.addAction(a1)
        self.changeTabMenu.addAction(a2)
        self.changeTabMenu.addAction(a3)
        self.tabsPerRowList.append(a1)
        self.tabsPerRowList.append(a2)
        self.tabsPerRowList.append(a3)

        for i in range(len(self.tabsPerRowList)):
            self.tabsPerRowList[i].setCheckable(True)
        self.tabsPerRowList[0].setChecked(True)

        self.tabsPerRowList[0].triggered.connect(lambda: self.changedTabsPerRow(0))
        self.tabsPerRowList[1].triggered.connect(lambda: self.changedTabsPerRow(1))
        self.tabsPerRowList[2].triggered.connect(lambda: self.changedTabsPerRow(2))

        quitAction = QAction("&Close", self)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.triggered.connect(self.close)
        file.addAction(quitAction)
    
    def changedTabsPerRow(self, ind):
        for i in range(len(self.tabsPerRowList)):
            if not i == ind:
                self.tabsPerRowList[i].setChecked(False)
        self.tabsPerRowList[ind].setChecked(True)
        self.centralWidget.openTabPage.changeTabsPerRow(ind + 3)
    
    def openRenameDialog(self):
        dialog = QDialog()
        layout = QVBoxLayout()
        textEdit = QLineEdit()
        textEdit.setPlaceholderText("Enter new name")

        def enterPressed():
            self.centralWidget.renamePage(textEdit.text())
            dialog.close()

        textEdit.returnPressed.connect(enterPressed)
        layout.addWidget(textEdit)
        dialog.setLayout(layout)
        dialog.exec_()

    def changeTitle(self, string):
        self.setWindowTitle(WINDOW_NAME + string)

    def close(self):
        self.centralWidget.driver.close()
        self.centralWidget.driver.quit()
        print('Exiting:::')
        qApp.quit()

if __name__ == '__main__':
    app = QApplication([])

    widget = PageManager()
    window = MainWindow(widget)
    widget.updateTitle()
    window.show()

    app.aboutToQuit.connect(window.close)
    #app.setStyle('macintosh')

    mainWindow = QMainWindow

    style = QPalette()
    style.setColor(QPalette.Window, QColor(53, 53, 53))
    style.setColor(QPalette.Background, QColor(53, 53, 53))
    style.setColor(QPalette.WindowText, Qt.red)
    style.setColor(QPalette.Base, QColor(25, 25, 25))
    style.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    style.setColor(QPalette.ToolTipBase, Qt.black)
    style.setColor(QPalette.ToolTipText, Qt.white)
    style.setColor(QPalette.Text, Qt.red)
    style.setColor(QPalette.Button, QColor(53, 53, 53))
    style.setColor(QPalette.ButtonText, QColor(42, 42, 42))
    style.setColor(QPalette.BrightText, Qt.red)
    style.setColor(QPalette.Link, QColor(42, 130, 218))
    style.setColor(QPalette.Highlight, QColor(42, 130, 218))
    style.setColor(QPalette.HighlightedText, Qt.black)
    style.setColor(QPalette.Light, QColor(53, 53, 53))
    app.setPalette(style)

    sys.exit(app.exec_())
