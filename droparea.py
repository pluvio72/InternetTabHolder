import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

MIN_FOR_CLOSE = 100

class DropArea(QLabel):
    #INITIALIZE SIGNALS
    imageLoaded = pyqtSignal(bool)
    tabDeleted = pyqtSignal(QWidget)
    tabAdded = pyqtSignal(QWidget, int)
    tabReordered = pyqtSignal(QWidget, int)
    
    def __init__(self, tabNumber, driver, minWidth, minHeight, aspectRatio, imageFolder):
        super().__init__()

        # CONNECT EVENTS (MOUSE/SLOTS & SIGNALS)
        self.destroyed.connect(self.onDestroy)
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

        self.tabNumber = tabNumber
        self.clear()

    def onDestroy():
        print('On destroy')

    def areaClicked(self, event):
        self.startClick = event.pos()
    
    #IF DRAG UP REMOVE TAB, IF CLICK OPEN URL
    def areaReleased(self, event):   
        self.endClick = event.pos()
        xDiff = self.endClick.x() - self.startClick.x()
        yDiff = abs(self.endClick.y() - self.startClick.y())

        if yDiff > MIN_FOR_CLOSE or abs(xDiff) > self.sizeHint().width():
            if yDiff > MIN_FOR_CLOSE:
                self.tabDeleted.emit(self)
            elif abs(xDiff) > self.sizeHint().width():
                index = (self.tabNumber-1) % 3
                #GET TABS TO MOVE E.G. -1 (1 LEFT) OR 2 (2 RIGHT)
                tabsToSwap = (int)(xDiff/self.sizeHint().width())
                left = True if (xDiff < 0) else False
                #GET PARENT WIDGET AND MOVE TAB
                parent = self.parent().layout().itemAt(0)
                parent.removeWidget(self)
                parent.insertWidget(index + tabsToSwap, self)
                
                #EMIT SIGNAL SO LIST CAN BE REORGANIZED AND CHAGNES SAVED TO FILE
                self.tabReordered.emit(self, tabsToSwap)
        else: 
            if self.taken: QDesktopServices.openUrl(QUrl(self.url))

    #SET TEXT TO DROP AND CHANGE COLOR
    def dragEnterEvent(self, event):
        if not self.taken:
            self.setText('Drop Here')
            self.setBackgroundRole(QPalette.Light)
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
            self.downloadImage()
            self.saveTab()
            event.acceptProposedAction()
            self.tabAdded.emit(self, self.tabNumber)
    
    #ON RESIZE UPDATE PIXMAP SIZE
    def resizeEvent(self, e):
        if self.pixmap() != None:
            self.setPixmap(self._pixmap.scaled(self.sizeHint(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setFixedHeight(self.sizeHint().height())

    #OVERLOAD SIZEHINT SO IT GETS SIZE OF PARENT LAYOUT CHILDREN / PARENT LAYOUT WIDTH
    def sizeHint(self):
        count = self.parent().layout().itemAt(0).count()
        width = self.parent().width() / count
        if width >= self.minWidth:
            return QSize(width, width*self.aspectRatio)
        else:
            return QSize(self.minWidth, self.minHeight)

    #LOAD TAB PIXMAP AND SET CLASS VARIABLES
    def load(self, url, imagePath, addTabAfter):
        self.taken = True
        self.url = url
        self.tabAdded.emit(self, self.tabNumber)
        self.imagePath = imagePath
        self._pixmap = QPixmap(os.path.join(self.imageFolder, imagePath)).scaled(self.sizeHint(), Qt.KeepAspectRatio)
        self.setPixmap(self._pixmap)
        if addTabAfter: self.imageLoaded.emit(False)

    #DOWNLOAD IMAGE FROM DRIVER
    def downloadImage(self):
        self.imagePath = str(self.url).replace('/', '') + '.png'
        self.driver.get(self.url)
        self.driver.save_screenshot(os.path.join(self.imageFolder, self.imagePath))
        self._pixmap = QPixmap(os.path.join(self.imageFolder, self.imagePath), '1')
        self.setPixmap(self._pixmap.scaled(self.sizeHint(), Qt.KeepAspectRatio))
        self.imageLoaded.emit(False)

    #SAVE TAB ENTRY TO FILE
    def saveTab(self):
        with open('tabs.txt', 'a') as f:
            info = self.url + ' ' + self.imagePath + ' ' + str(self.tabNumber) + '\n'
            f.write(info)

    #CLEAR TAB AND SET TEXT
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