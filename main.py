import os
import pkgutil
import sys
import json
from shutil import copyfile

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPalette
from PyQt5.QtWidgets import (QAction, QApplication, QColorDialog, QDialog,
                             QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QPushButton, QVBoxLayout, qApp,
                             QSizePolicy, QLayout, QComboBox)

from dropsitewindow import DropSiteWindow
from pagemanager import PageManager
from tabsettings import MIN_TAB_HEIGHT, MIN_TAB_WIDTH, WINDOW_NAME, SETTINGS_FILE_NAME

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

palette_dict = {
    'window': QPalette.Window,
    'windowText': QPalette.WindowText,
    'text': QPalette.Text,
    'base': QPalette.Base,
    'alternateBase': QPalette.AlternateBase,
    'highlight': QPalette.Highlight,
    'highlightedText': QPalette.HighlightedText,
    'link': QPalette.Link,
    'toolTipText': QPalette.ToolTipText,
    'toolTipBase': QPalette.ToolTipBase,
    'brightText': QPalette.BrightText,
    'button': QPalette.Button,
    'buttonText': QPalette.ButtonText,
    'light': QPalette.Light
}   

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

        self.checkSettings()

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def checkSettings(self):
        if os.path.isfile(os.path.join(os.getcwd(), SETTINGS_FILE_NAME)):
            with open(SETTINGS_FILE_NAME, 'r') as f:
                data = f.readlines()[0]
                self.settings_data = json.loads(data)
                for index, item in enumerate(self.settings_data):
                    if index < len(self.settings_data)-1:
                        self.setPaletteColor(item)
        else:
            self.settings_data = {}
            self.settings_data['windowText'] = self.palette().windowText().color().getRgb()
            self.settings_data['text'] = self.palette().text().color().getRgb()
            self.settings_data['window'] = self.palette().window().color().getRgb()
            self.settings_data['highlight'] = self.palette().highlight().color().getRgb()
            self.settings_data['brightText'] = self.palette().brightText().color().getRgb()
            self.settings_data['button'] = self.palette().button().color().getRgb()
            self.settings_data['buttonText'] = self.palette().buttonText().color().getRgb()

            self.settings_data['light'] = self.palette().light().color().getRgb()
            self.settings_data['highlightedText'] = self.palette().highlightedText().color().getRgb()
            self.settings_data['link'] = self.palette().link().color().getRgb()
            self.settings_data['base'] = self.palette().base().color().getRgb()
            self.settings_data['alternateBase'] = self.palette().alternateBase().color().getRgb()
            self.settings_data['toolTipText'] = self.palette().toolTipText().color().getRgb()
            self.settings_data['toolTipBase'] = self.palette().toolTipBase().color().getRgb()
            self.settings_data['selectedTheme'] = 'None'

            with open(SETTINGS_FILE_NAME, 'w') as f:
                json.dump(self.settings_data, f)
    
    def updateSettings(self, item, value):
        self.settings_data[item] = value
        with open(SETTINGS_FILE_NAME, 'w') as f:
            json.dump(self.settings_data, f)

    # SET PALETTE COLOR FROM JSON DATA SAVED IN SETTNGS FILE
    def setPaletteColor(self, item):
        global palette_dict
        style = QPalette()
        if len(self.settings_data[item]) > 3: style.setColor(palette_dict[item], QColor(self.settings_data[item][0], self.settings_data[item][1], self.settings_data[item][2], self.settings_data[item][3]))
        else: style.setColor(palette_dict[item], QColor(self.settings_data[item][0], self.settings_data[item][1], self.settings_data[item][2]))
        app.setPalette(style)
    
    def changeTheme(self, themeName):
        themeName = themeName.lower() + '.json'
        with open(themeName, 'r') as f:
            data = f.readlines()[0]
            self.settings_data = json.loads(data)

        self.settings_data['selectedTheme'] = themeName

        for index, item in enumerate(self.settings_data):
            if index < len(self.settings_data)-1:
                self.setPaletteColor(item)
        with open(SETTINGS_FILE_NAME, 'w') as f:
            json.dump(self.settings_data, f)

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
        mainSub = QVBoxLayout()
        subLayout = QVBoxLayout()
        subLayout2 = QVBoxLayout()
        dialog.setLayout(mainSub)
        dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        mainLayout.addLayout(subLayout)
        mainLayout.addLayout(subLayout2)
        mainSub.addLayout(mainLayout)

        def addColorItem(colorString, colorInt, string, layout):
            def selectColor(label):
                color = QColorDialog.getColor()
                label.setStyleSheet('QPushButton { background-color: ' + 'rgba' + str(color.getRgb()) + '; border: 1px solid black; }')
                style = QPalette()
                style.setColor(colorInt, color)
                app.setPalette(style)
                self.updateSettings(string, color.getRgb())

            subsub = QHBoxLayout()
            label = QPushButton('')
            label.setAutoFillBackground(True)
            label.setMinimumWidth(55)
            label.setStyleSheet('QPushButton { background-color: ' + colorString + '; border: 1px solid black; }')
            label.clicked.connect(lambda: selectColor(label))
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
        addColorItem(prefix+str(self.palette().text().color().getRgb()), QPalette.Text, 'text', 1)
        addColorItem(prefix+str(self.palette().window().color().getRgb()), QPalette.Window, 'window', 1)
        addColorItem(prefix+str(self.palette().windowText().color().getRgb()), QPalette.WindowText, 'windowText', 1)
        addColorItem(prefix+str(self.palette().highlight().color().getRgb()), QPalette.Highlight, 'highlight', 1)
        addColorItem(prefix+str(self.palette().brightText().color().getRgb()), QPalette.BrightText, 'brightText', 1)
        addColorItem(prefix+str(self.palette().button().color().getRgb()), QPalette.Button, 'button', 1)
        addColorItem(prefix+str(self.palette().buttonText().color().getRgb()), QPalette.ButtonText, 'buttonText', 1)

        addColorItem(prefix+str(self.palette().light().color().getRgb()), QPalette.Light, 'light', 2)
        addColorItem(prefix+str(self.palette().highlightedText().color().getRgb()), QPalette.HighlightedText, 'highlightedText', 2)
        addColorItem(prefix+str(self.palette().link().color().getRgb()), QPalette.Link, 'link', 2)
        addColorItem(prefix+str(self.palette().base().color().getRgb()), QPalette.Base, 'base', 2)
        addColorItem(prefix+str(self.palette().alternateBase().color().getRgb()), QPalette.AlternateBase, 'alternateBase', 2)
        addColorItem(prefix+str(self.palette().toolTipText().color().getRgb()), QPalette.ToolTipText, 'toolTipText', 2)
        addColorItem(prefix+str(self.palette().toolTipBase().color().getRgb()), QPalette.ToolTipBase, 'toolTipBase', 2)

        p = QHBoxLayout()
        dropdown = QComboBox()
        if self.settings_data['selectedTheme'] != 'None':
            if self.settings_data['selectedTheme'] == 'Light':
                dropdown.addItem('Light')
                dropdown.addItem('Dark')
            else:
                dropdown.addItem('Dark')
                dropdown.addItem('Light')
        else:
            dropdown.addItem('Light')
            dropdown.addItem('Dark')
        dropdown.currentTextChanged.connect(lambda data: self.changeTheme(data))
        p.addWidget(dropdown)
        mainSub.addLayout(p)

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

#settings_data = {}
#settings_data['window'] = (53, 53, 53)
#settings_data['windowText'] = (255, 255, 255)
#settings_data['base'] = (25, 25, 25)
#settings_data['alternateBase'] = (53, 53, 53)
#settings_data['toolTipBase'] = (0, 0, 0)
#settings_data['toolTipText'] = (255, 255, 255)
#
#settings_data['text'] = (255, 255, 255)
#settings_data['button'] = (53, 53, 53)
#settings_data['buttonText'] = (42, 42, 42)
#settings_data['brightText'] = (255, 255, 255)
#settings_data['link'] = (42, 130, 218)
#settings_data['highlight'] = (42, 130, 218)
#settings_data['highlightedText'] = (0, 0, 0)
#settings_data['light'] = (53, 53, 53)
#
#with open(SETTINGS_FILE_NAME, 'w') as f:
#    json.dump(settings_data, f)
    

sys.exit(app.exec_())
