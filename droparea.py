import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from addtabdialog import AddTabDialog
import constants

MIN_FOR_CLOSE = 100

class DropArea(QLabel):
    # INITIALIZE SIGNALS
    tabReordered = pyqtSignal(QWidget, int)
    tabAdded = pyqtSignal(QWidget, int)
    tabDeleted = pyqtSignal(QWidget)
    imageLoaded = pyqtSignal()
    
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

        self.tabNumber = tabNumber
        self.defaultTab('Drag URL Here')

    # ON MOUSE ENTER
    def enterEvent(self, event):
        if self.taken:
            self.setToolTip(self.url)
            self.setToolTipDuration(1000)
        else: self.setBackgroundRole(QPalette.Highlight)
    
    # ON MOUSE LEAVE
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
            if yDiff > MIN_FOR_CLOSE:self.tabDeleted.emit(self)
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
                        parent = constants.tabRows[int((self.tabNumber-1)/constants.tabsPerRow)].layout()
                        parent.removeWidget(self)
                        parent.insertWidget(index + tabsToSwap, self)
                        # EMIT SIGNAL SO LIST CAN BE REORGANIZED AND CHAGNES SAVED TO FILE
                        self.tabReordered.emit(self, tabsToSwap)
        # OPEN TAB IN BROWSER OR IF EMPTY ENTER URL MANUALLY
        else: 
            if self.taken: QDesktopServices.openUrl(QUrl(self.url))
            else: dialog = AddTabDialog(self)

        # RESET FRAME WHEN NOT CLICKED
        if self.taken:
            self.setFrameStyle(QFrame.NoFrame)
            self.setLineWidth(2)

    # SET TEXT TO DROP AND CHANGE COLOR
    def dragEnterEvent(self, event):
        if not self.taken:
            self.highlightTab()
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        event.setDropAction(Qt.MoveAction)

    def dragLeaveEvent(self, event):
        self.defaultTab() 
        event.accept()
    
    #IF NOT TAKEN GET IMAGE AND SAVE TAB
    def dropEvent(self, event):
        if not self.taken:
            self.defaultTab('Loading...')
            self.taken = True
            self.url = event.mimeData().text()

            ###
            ### CHECK URL IN TABLIST -> USE LOCAL IMAGE
            ### CHECK URL IN ARCHIVED TAB LIST -> USE LOCAL IMAGE
            ### IF NEW URL -> DOWNLOAD IMAGE
            ### SET PIXMAP FROM _PIXMAP
            ### SAVE TAB TO FILE
            ### ADD TAB TO TAB LIST
            ###
            ### MAKE SURE YOU CANT GET DUPLICATE TAB IN LIST AND DUPLICATE ARCHIVED TAB
            ###
            duplicateTab = self.checkDuplicateTab(self.url, 'tabs.txt')
            duplicateArchiveTab = self.checkDuplicateTab(self.url, '.tabs.txt')
            if duplicateTab: self.setDuplicateTab(self.url)
            elif duplicateArchiveTab: self.setDuplicateArchiveTab(self.url)
            else: self.downloadImage(self.url)
            self.setLocalPixmap()
            self.saveTab()
            self.tabAdded.emit(self, self.tabNumber)
            self.addCloseButton()
            event.acceptProposedAction()
    
    # ON RESIZE UPDATE PIXMAP SIZE
    def resizeEvent(self, e):
        if self.pixmap() != None: self.setPixmap(self._pixmap.scaled(self.sizeHint(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setFixedHeight(self.sizeHint().height())

    # OVERLOAD SIZEHINT SO IT GETS SIZE OF PARENT LAYOUT CHILDREN / PARENT LAYOUT WIDTH
    def sizeHint(self):
        # WHEN CLEARING TABS SOMETIMES THE ROW IS NOT THERE WHEN RESIZE EVENT OCCURS
        if self.parent() != None:
            if self.parent().layout().itemAt(0).count() > 0:
                hasAttr = hasattr(self.parent().layout().itemAt(0), "count")
                if hasAttr:
                    count = self.parent().layout().itemAt(0).count()
                    width = self.parent().width() / count
                    if width >= self.minWidth:
                        return QSize(width, width*self.aspectRatio)
        return QSize(self.minWidth, self.minHeight)

    def addCloseButton(self):
        button = QPushButton("x", self)
        button.move(0, 0)
        button.show()
        button.clicked.connect(lambda: self.tabDeleted.emit(self))

    # LOAD TAB PIXMAP AND SET CLASS VARIABLES
    def load(self, url, imagePath):
        self.taken = True
        self.url = url
        ### BUG: WHEN LOADING ARCHIVED TAB FROM MANUAL ADD
        setImagePath = False
        if self.checkFileExists('.tabs.txt'):
            with open('.tabs.txt', 'r') as f:
                for line in f:
                    currentUrl = line.split('\n')[0].split(' ')[0]
                    currentPath = line.split('\n')[0].split(' ')[1]
                    if currentUrl == url:
                        if not os.path.isfile(os.path.join(self.imageFolder, currentPath[1:])): os.rename(os.path.join(self.imageFolder, currentPath), os.path.join(self.imageFolder, currentPath[1:]))
                        self.imagePath = currentPath[1:]  
                        setImagePath = True
        if not setImagePath: self.imagePath = imagePath
        self._pixmap = QPixmap(os.path.join(self.imageFolder, self.imagePath))
        self.setPixmap(self._pixmap.scaled(self.sizeHint(), Qt.KeepAspectRatio))
        self.tabAdded.emit(self, self.tabNumber)
        self.addCloseButton()

    # DOWNLOAD IMAGE FROM DRIVER
    def downloadImage(self, url):
        self.imagePath = str(url).replace('/', '') + '.png'
        self.driver.get(url)
        path = os.path.join(self.imageFolder, self.imagePath)
        self.driver.save_screenshot(path)
        self._pixmap = QPixmap(path, '1')
    
    # SET PIXMAP FROM _PIXMAP
    def setLocalPixmap(self):
        self.setPixmap(self._pixmap.scaled(self.sizeHint(), Qt.KeepAspectRatio))
        constants.loadedTabCount += 1
        self.imageLoaded.emit()

    # CHECK IF FILE EXISTS AND IF ITS NOT EMPTY
    def checkFileExists(self, fileName):
        exists = os.path.isfile(os.path.join(os.getcwd(), fileName))
        notEmpty = False
        if exists:
            notEmpty = True if (os.path.getsize(os.path.join(os.getcwd(), fileName)) > 0) else False
        return (exists and notEmpty)
    
    # CHECK IF URL IS IN FILENAME
    def checkDuplicateTab(self, url, fileName):
        if self.checkFileExists(fileName):
            with open(fileName, 'r') as f:
                for line in f:
                    if url == line.split(' ')[0]: return True
        return False
    
    # CHECK THROUGH TABS FILE AND SET IMAGEPATH AND PIXMAP IF URL EXISTS
    def setDuplicateTab(self, url):
        with open('tabs.txt', 'r') as f:
            for line in f:
                if url == line.split(' ')[0]: 
                    imagePath = line.split(' ')[1]
                    self.imagePath = imagePath
                    self._pixmap = QPixmap(os.path.join(self.imageFolder, imagePath), '1')
    
    # CHECK THROUGH ARCHIVED TABS FILE AND SET IMAGEPATH AND PIXMAP IF URL EXISTS
    def setDuplicateArchiveTab(self, url):
        with open('.tabs.txt', 'r') as f:
            for line in f:
                if url == line.split(' ')[0]:
                    imagePath = line.split('\n')[0].split(' ')[1]
                    # RENAME IMAGE TO MAKE IT NOT HIDDEN
                    os.rename(os.path.join(self.imageFolder, imagePath), os.path.join(self.imageFolder, imagePath[1:]))
                    self.imagePath = imagePath[1:]
                    self._pixmap = QPixmap(os.path.join(self.imageFolder, self.imagePath), '1')

    # SAVE TAB ENTRY TO FILE
    def saveTab(self):
        with open('tabs.txt', 'a') as f:
            info = self.url + ' ' + self.imagePath + ' ' + str(self.tabNumber) + '\n'
            f.write(info)

    def setTaken(self, url):
        self.taken = True
        self.url = url
    
    def addedLoaded(self):
        self.tabAdded.emit(self, self.tabNumber)
        self.imageLoaded.emit()

    def defaultTab(self, text):
        self.setText(text)
        self.setBackgroundRole(QPalette.Dark)
    
    def highlightTab(self):
        self.setBackgroundRole(QPalette.Mid)
        self.setText('Drop Here')