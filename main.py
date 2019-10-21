import os
import pkgutil
import sys
from shutil import copyfile

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPalette
from PyQt5.QtWidgets import (QAction, QApplication, QColorDialog, QDialog,
                             QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QPushButton, QVBoxLayout, qApp,
                             QSizePolicy, QLayout)

from dropsitewindow import DropSiteWindow
from pagemanager import PageManager
from tabsettings import MIN_TAB_HEIGHT, MIN_TAB_WIDTH, WINDOW_NAME

if os.path.isfile('/Users/maksie/Documents/Coding/Python/Projects/PyChromeTabs/mylog.txt'):
    os.remove('/Users/maksie/Documents/Coding/Python/Projects/PyChromeTabs/mylog.txt')
def writeLog(text):
    with open('/Users/maksie/Documents/Coding/Python/Projects/PyChromeTabs/mylog.txt', 'a') as f:
        f.write(text)


# SET CURRENT WORKING DIRECTORY
#current_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
if not os.path.isfile('chromedriver_mac_77') and not os.path.isfile('chromedriver_win32_77'):
    current_dir = os.path.dirname(sys.executable)
    os.chdir(current_dir)
if not os.path.exists(os.path.join(os.getcwd(), '_data')):
    os.mkdir(os.path.join(os.getcwd(), '_data'))
os.chdir('_data')

run_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# SET DRIVER PATH ENVIRONMENT VARIABLE
driver_path = 'chromedriver_mac_77' if sys.platform == 'darwin' else 'chromedriver_win32_77'
if not os.path.isfile(os.path.join(os.getcwd(), '../'+driver_path)): os.environ['chrome_driver'] = os.path.abspath(os.path.join(run_path, driver_path))
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

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

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

        self.stayTopAction = QAction("Stay On Top", self)
        self.stayTopAction.setShortcut("Ctrl+Shift+A")
        self.stayTopAction.setCheckable(True)
        self.stayTopAction.setChecked(True)
        self.stayTopActionChecked = True
        self.stayTopAction.triggered.connect(self.stayTopToggle)
        file.addAction(self.stayTopAction)

        themeMenuAction = QAction("Theme", self)
        themeMenuAction.setShortcut("Ctrl+T")
        themeMenuAction.triggered.connect(self.openThemeMenu)
        file.addAction(themeMenuAction)

        #helpAction = QAction("Help", self)
        #helpAction.setShortcut("Ctrl+Shift+H")
        #helpAction.triggered.connect(self.showHelp)
        #file.addAction(helpAction)

        quitAction = QAction("&Close", self)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.triggered.connect(self.close)
        file.addAction(quitAction)
    
    # OPEN THEME MENU
    def openThemeMenu(self):
        dialog = QDialog()
        mainLayout = QHBoxLayout()
        subLayout = QVBoxLayout()
        subLayout2 = QVBoxLayout()
        dialog.setLayout(mainLayout)
        dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        mainLayout.addLayout(subLayout)
        mainLayout.addLayout(subLayout2)

        def addColorItem(colorString, string, layout):
            subsub = QHBoxLayout()
            label = QLabel('')
            label.setAutoFillBackground(True)
            label.setMinimumWidth(55)
            label.setStyleSheet('QLabel { background-color: ' + colorString + '; }')
            label.setFrameStyle(QFrame.Panel)
            label.mouseDoubleClickEvent.connect(lambda: print('double clicked'))
            textLabel = QLabel(string)
            textLabel.setMinimumWidth(100)
            subsub.addWidget(label)
            subsub.addWidget(textLabel)
            subsub.setSizeConstraint(QLayout.SetMaximumSize)
            if layout == 1: subLayout.addLayout(subsub)
            else: subLayout2.addLayout(subsub)

        subLayout.setContentsMargins(20, 20, 20, 20)
        subLayout2.setContentsMargins(20, 20, 20, 20)

        prefix = 'rgba'
        addColorItem(prefix+str(self.palette().text().color().getRgb()), 'Text', 1)
        #addColorItem(prefix+str(self.palette().background().color().getRgb()), 'Background', 1)
        addColorItem(prefix+str(self.palette().window().color().getRgb()), 'Window', 1)
        addColorItem(prefix+str(self.palette().windowText().color().getRgb()), 'Window Text', 1)
        addColorItem(prefix+str(self.palette().highlight().color().getRgb()), 'Highlight', 1)
        addColorItem(prefix+str(self.palette().brightText().color().getRgb()), 'Bright Text', 1)
        addColorItem(prefix+str(self.palette().button().color().getRgb()), 'Button', 1)
        addColorItem(prefix+str(self.palette().buttonText().color().getRgb()), 'Button Text', 1)

        addColorItem(prefix+str(self.palette().light().color().getRgb()), 'Light', 2)
        addColorItem(prefix+str(self.palette().highlightedText().color().getRgb()), 'Highlighted Text', 2)
        addColorItem(prefix+str(self.palette().link().color().getRgb()), 'Link', 2)
        addColorItem(prefix+str(self.palette().base().color().getRgb()), 'Base', 2)
        addColorItem(prefix+str(self.palette().alternateBase().color().getRgb()), 'Alternate Base', 2)
        addColorItem(prefix+str(self.palette().toolTipText().color().getRgb()), 'TooltipText', 2)
        addColorItem(prefix+str(self.palette().toolTipBase().color().getRgb()), 'TooltipBase', 2)

        dialog.exec_()

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
    
    # CHANGE WHETHER WINDOW STAYS ON TOP
    def stayTopToggle(self):
        self.stayTopActionChecked = not self.stayTopActionChecked
        self.stayTopAction.setChecked(self.stayTopActionChecked)
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowStaysOnTopHint)
        self.show()

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
        dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
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

#style = QPalette()
#style.setColor(QPalette.Window, QColor(53, 53, 53))
#style.setColor(QPalette.Background, QColor(53, 53, 53))
#style.setColor(QPalette.WindowText, Qt.red)
#style.setColor(QPalette.Base, QColor(25, 25, 25))
#style.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
#style.setColor(QPalette.ToolTipBase, Qt.black)
#style.setColor(QPalette.ToolTipText, Qt.white)
#style.setColor(QPalette.Text, Qt.red)
#style.setColor(QPalette.Button, QColor(53, 53, 53))
#style.setColor(QPalette.ButtonText, QColor(42, 42, 42))
#style.setColor(QPalette.BrightText, Qt.red)
#style.setColor(QPalette.Link, QColor(42, 130, 218))
#style.setColor(QPalette.Highlight, QColor(42, 130, 218))
#style.setColor(QPalette.HighlightedText, Qt.black)
#style.setColor(QPalette.Light, QColor(53, 53, 53))
#app.setPalette(style)

sys.exit(app.exec_())
