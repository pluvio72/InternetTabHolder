from PyQt5.QtWidgets import QMainWindow, QAction, QDialog, QVBoxLayout, QPushButton, QLineEdit, QApplication, qApp
from tabsettings import MIN_TAB_WIDTH, MIN_TAB_HEIGHT, WINDOW_NAME
from PyQt5.QtGui import QPalette, QColor, QIcon
from dropsitewindow import DropSiteWindow
from pagemanager import PageManager
from PyQt5.QtCore import Qt
import sys
import os

# SET CURRENT WORKING DIRECTORY
#current_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
if not os.path.isfile('chromedriver_mac_77') and not os.path.isfile('chromedriver_win32_77'):
    current_dir = os.path.dirname(sys.executable)
    os.chdir(current_dir)
if not os.path.exists(os.path.join(os.getcwd(), '_data')):
    os.mkdir(os.path.join(os.getcwd(), '_data'))
os.chdir('_data')

# SET DRIVER PATH ENVIRONMENT VARIABLE
driver_path = 'chromedriver_mac_77' if sys.platform == 'darwin' else 'chromedriver_win32_77'
if not os.path.isfile(os.path.join(os.getcwd(), '../'+driver_path)): os.environ['chrome_driver'] = os.path.abspath(os.path.join(os.getcwd(), '../../../../../'+driver_path))
else: os.environ['chrome_driver'] = os.path.abspath('../'+driver_path)

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

        #self.setWindowFlags(Qt.WindowStaysOnTopHint)

    # CREATE ALL MENU BUTTONS -> SET SHORTCUTS -> CONNECT SIGNALS/SLOTS
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

        nextPageAction = QAction("Next Page", self)
        nextPageAction.setShortcut("Ctrl+Right")
        nextPageAction.triggered.connect(self.centralWidget.nextPage)
        file.addAction(nextPageAction)

        prevPageAction = QAction("Prev Page", self)
        prevPageAction.setShortcut("Ctrl+Left")
        prevPageAction.triggered.connect(self.centralWidget.prevPage)
        file.addAction(prevPageAction)

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

        helpAction = QAction("Help", self)
        helpAction.setShortcut("Ctrl+Shift+H")
        helpAction.triggered.connect(self.showHelp)
        file.addAction(helpAction)

        quitAction = QAction("&Close", self)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.triggered.connect(self.close)
        file.addAction(quitAction)
    
    # SET ALL OTHER TAB NUMBER OPTIONS TO UNCHECKED -> CHANGE TABS PER ROW ON CURRENT PAGE
    def changedTabsPerRow(self, ind):
        for i in range(len(self.tabsPerRowList)):
            if not i == ind:
                self.tabsPerRowList[i].setChecked(False)
        self.tabsPerRowList[ind].setChecked(True)
        self.centralWidget.openTabPage.changeTabsPerRow(ind + 3)
    
    # CMD+SHIFT+H SHOWS HELP DIALOG WITH HOW TO USE THE TAB HOLDER
    def showHelp(self):
        dialog = QDialog()
        layout = QVBoxLayout()
        layout.addWidget(QPushButton("Help"))
        dialog.setLayout(layout)
        dialog.exec_()

    # CMD+R OPENS DIALOG WITH TEXT EDIT WHICH RENAMES TAG PAGE VARIABLE -> RENAMES WINDOW -> UPDATES ENTRY IN PAGENAMES FILE
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

    # CHANGES WINDOW TITLE
    def changeTitle(self, string):
        self.setWindowTitle(WINDOW_NAME + string)

    def close(self):
        self.centralWidget.driver.close()
        self.centralWidget.driver.quit()
        qApp.quit()

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
