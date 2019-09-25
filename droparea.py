import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import constants

MIN_FOR_CLOSE = 100

class DropArea(QLabel):
    # INITIALIZE SIGNALS
    imageLoaded = pyqtSignal(bool)
    tabDeleted = pyqtSignal(QWidget)
    tabAdded = pyqtSignal(QWidget, int)
    tabReordered = pyqtSignal(QWidget, int)
    
    def __init__(self, tabNumber, driver, minWidth, minHeight, aspectRatio, imageFolder):
        super().__init__()

        # CONNECT EVENTS (MOUSE/SLOTS & SIGNALS)
        self.mousePressEvent = self.areaClicked
        self.mouseReleaseEvent = self.areaReleased

        # INITIALIZE CLASS VARIABLES
        self.taken = False
        self.startClick = 0
        self.endClick = 0
        self.aspectRatio = aspectRatio
        self.minWidth = minWidth
        self.minHeight = minHeight
        self.imageFolder = imageFolder
        self.driver = driver

        self.setMinimumSize(self.minWidth, self.minHeight)
        self.setFrameStyle(QFrame.Plain)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)

        button = QPushButton("x", self)
        button.move(0, 0)
        button.show()
        button.clicked.connect(lambda: self.tabDeleted.emit(self))

        self.tabNumber = tabNumber
        self.clear()

    def enterEvent(self, event):
        if self.taken:
            self.setToolTip(self.url)
            self.setToolTipDuration(1000)
        else: self.setBackgroundRole(QPalette.Highlight)
    
    def leaveEvent(self, event):
        if not self.taken: self.setBackgroundRole(QPalette.Dark)

    def areaClicked(self, event):
        self.startClick = event.pos()
        if self.taken:
            self.setFrameStyle(QFrame.Plain | QFrame.Box)
            self.setLineWidth(5)
    
    # IF DRAG UP REMOVE TAB, IF CLICK OPEN URL
    def areaReleased(self, event):   
        self.endClick = event.pos()
        xDiff = self.endClick.x() - self.startClick.x()
        yDiff = abs(self.endClick.y() - self.startClick.y())

        # IF X/Y DELTA GREATER THAN RESPECTIVE MINS REORDER/DELETE
        if yDiff > MIN_FOR_CLOSE or abs(xDiff) > self.sizeHint().width():
            # IF Y DELTA GREATER THAN MIN CLOSE/DELETE TAB
            if yDiff > MIN_FOR_CLOSE:
                self.tabDeleted.emit(self)
            # IF X DELTA GREATER THAN TAB WIDTH REORDER TAB
            elif abs(xDiff) > self.sizeHint().width():
                if self.taken:
                    index = (self.tabNumber-1) % 3
                    # GET TABS TO MOVE E.G. -1 (1 LEFT) OR 2 (2 RIGHT)
                    tabsToSwap = (int)(xDiff/self.sizeHint().width())
                    left = True if (xDiff < 0) else False
                    # IF NOT LEFT MOST TAB AND TRYING TO DRAG LEFT
                    if not (index == 0 and left):
                        #GET PARENT WIDGET AND MOVE TAB
                        parent = self.parent().layout().itemAt(0)
                        parent.removeWidget(self)
                        parent.insertWidget(index + tabsToSwap, self)
                    
                        # EMIT SIGNAL SO LIST CAN BE REORGANIZED AND CHAGNES SAVED TO FILE
                        self.tabReordered.emit(self, tabsToSwap)
        # OPEN TAB IN BROWSER OR IF EMPTY ENTER URL MANUALLY
        else: 
            if self.taken: QDesktopServices.openUrl(QUrl(self.url))
            else:
                dialog = QDialog()
                layout = QVBoxLayout()
                label = QLabel("Enter URL: ")
                label.setAlignment(Qt.AlignCenter)
                textEdit = QLineEdit("https://www.google.com")
                textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                textEdit.setFrame(QFrame.NoFrame)
                button = QPushButton("Add URL")

                def dialogButton():
                    self.loadFromUrl(textEdit.text())
                    dialog.deleteLater()
                button.clicked.connect(dialogButton)

                urlList = QListWidget()
                path = os.path.join(os.getcwd(), '.tabs.txt')
                if os.path.isfile(path):
                    if os.path.getsize(path):
                        with open('.tabs.txt', 'r') as f:
                            lines = f.readlines()
                            for line in lines:
                                cur = line.split('\n')[0]
                                # GET URL FROM LINE (URL IMAGEPATH)
                                current = QListWidgetItem(cur.split(' ')[0])
                                urlList.addItem(current)

                urlList.currentItemChanged.connect(lambda current, previous: textEdit.setText(current.text()))

                layout.addWidget(label)
                layout.addWidget(textEdit)
                layout.addWidget(urlList)
                layout.addWidget(button)
                dialog.setWindowModality(Qt.ApplicationModal)
                dialog.setWindowTitle("Add Manually")
                dialog.setLayout(layout)
                dialog.exec_()
        
        if self.taken:
            self.setFrameStyle(QFrame.NoFrame)
            self.setLineWidth(2)

    # SET TEXT TO DROP AND CHANGE COLOR
    def dragEnterEvent(self, event):
        if not self.taken:
            self.setText('Drop Here')
            self.setBackgroundRole(QPalette.Mid)
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        event.setDropAction(Qt.MoveAction)

    def dragLeaveEvent(self, event):
        self.clear() 
        event.accept()
    
    #IF NOT TAKEN GET IMAGE AND SAVE TAB
    def dropEvent(self, event):
        if not self.taken:
            self.taken = True
            self.url = event.mimeData().text()
            self.setText('Loading...')
            self.setBackgroundRole(QPalette.Dark)

            ### HANDLE EXCEPTIONS WERE PAGES ARE BLOCKED OR NETWORK DOESNT WORK ETC
            ### WHEN GOING BACK ONLINE LOAD IMAGE??
            self.downloadImage()
            self.saveTab()
            event.acceptProposedAction()
            # CONNECTED TO ADD TAB TO LIST
            self.tabAdded.emit(self, self.tabNumber)
    
    # ON RESIZE UPDATE PIXMAP SIZE
    def resizeEvent(self, e):
        if self.pixmap() != None:
            self.setPixmap(self._pixmap.scaled(self.sizeHint(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setFixedHeight(self.sizeHint().height())

    # OVERLOAD SIZEHINT SO IT GETS SIZE OF PARENT LAYOUT CHILDREN / PARENT LAYOUT WIDTH
    def sizeHint(self):
        # WHEN CLEARING TABS SOMETIMES THE ROW IS NOT THERE WHEN RESIZE EVENT OCCURS
        if self.parent() != None:
            hasAttr = hasattr(self.parent().layout().itemAt(0), "count")
            if hasAttr:
                count = self.parent().layout().itemAt(0).count()
                width = self.parent().width() / count
                if width >= self.minWidth:
                    return QSize(width, width*self.aspectRatio)
        return QSize(self.minWidth, self.minHeight)

    # LOAD TAB PIXMAP AND SET CLASS VARIABLES
    def load(self, url, imagePath, addTabAfter):
        self.taken = True
        self.url = url
        self.tabAdded.emit(self, self.tabNumber)
        self.imagePath = imagePath
        self._pixmap = QPixmap(os.path.join(self.imageFolder, imagePath)).scaled(self.sizeHint(), Qt.KeepAspectRatio)
        self.setPixmap(self._pixmap)
        # CONNECTED TO NEWTAB
        if addTabAfter: self.imageLoaded.emit(False)

    # LOAD FUNCTION OVERLOAD WITH ONLY URL FOR MANUALLY ADDNG TAB
    def loadFromUrl(self, url):
        self.taken = True
        self.url = url
        self.imagePath = str(url.replace('/','') + '.png')

        if os.path.isfile('.tabs.txt') and os.path.getsize('.tabs.txt') > 0:
            with open('.tabs.txt', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    cur = line.split('\n')[0]
                    curUrl = cur.split(' ')[0]
                    imagePath = cur.split(' ')[1]
                    if curUrl == url:
                        if not os.path.isfile(os.path.join(self.imageFolder, imagePath[1:])):
                            os.rename(os.path.join(self.imageFolder, imagePath), os.path.join(self.imageFolder, imagePath[1:]))
                        self._pixmap = QPixmap(os.path.join(self.imageFolder, imagePath[1:], '1'))
                        self.imagePath = imagePath[1:]
                        self.url = url
                        self.setPixmap(self._pixmap.scaled(self.sizeHint(), Qt.KeepAspectRatio))
        else:
            if not self.checkDuplicate(url):
                self.driver.get(url)
                self.driver.save_screenshot(os.path.join(self.imageFolder, self.imagePath))
        self.tabAdded.emit(self, self.tabNumber)
        self.saveTab()
        self.setLocalPixmap()

    # DOWNLOAD IMAGE FROM DRIVER
    def downloadImage(self):
        self.imagePath = str(self.url).replace('/', '') + '.png'
        if not self.checkDuplicate(self.url):
            self.driver.get(self.url)
            self.driver.save_screenshot(os.path.join(self.imageFolder, self.imagePath))
        self.setLocalPixmap()
    
    # SET PIXMAP FROM IMAGEPATH MEMBER VARIABLE AND ADD NEW TAB AFTER
    def setLocalPixmap(self):
        self._pixmap = QPixmap(os.path.join(self.imageFolder, self.imagePath), '1')
        self.setPixmap(self._pixmap.scaled(self.sizeHint(), Qt.KeepAspectRatio))
        self.imageLoaded.emit(False)


    def checkDuplicate(self, url):
        for tab in constants.tabList:
            if tab.url == url:
                return True
        return False

    # SAVE TAB ENTRY TO FILE
    def saveTab(self):
        with open('tabs.txt', 'a') as f:
            info = self.url + ' ' + self.imagePath + ' ' + str(self.tabNumber) + '\n'
            f.write(info)

    # CLEAR TAB AND SET TEXT
    def clear(self):
        self.setText('Drop URL')
        self.setBackgroundRole(QPalette.Dark)

##class ThreadClass(QThread):
##    done = pyqtSignal()
##
##    def __init__(self, url, parent=None):
##        super(ThreadClass, self).__init__(parent)
##        self.url = url
##
##    def run(self):
##        options = Options()
##        options.headless = True
##        driver = webdriver.Firefox(options=options, executable_path='./geckodriver')
##        driver.get(self.url)
##        driver.save_screenshot('1.jpg')
##        driver.quit()
##        self.done.emit()