from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem, QSizePolicy, QFrame
from PyQt5.QtCore import Qt
import threading
import os

class AddTabDialog(QDialog):
    def __init__(self, tab):
        super().__init__()
        self.tab = tab
        self.layout = QVBoxLayout()
        self.label = QLabel("Enter URL: ")
        self.label.setAlignment(Qt.AlignCenter)
        self.textEdit = QLineEdit("https://www.google.com")
        self.textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.textEdit.setFrame(QFrame.NoFrame)
        self.button = QPushButton("Add URL")
        self.button.clicked.connect(self.addUrl)

        self.urlList = QListWidget()
        path = os.path.join(os.getcwd(), self.tab.archiveTabFileName)
        if os.path.isfile(path):
            if os.path.getsize(path) > 0:
                with open(self.tab.archiveTabFileName) as f:
                    lines = f.readlines()
                    for line in lines:
                        cur = line.split('\n')[0]
                        current = QListWidgetItem(cur.split(' ')[0])
                        self.urlList.addItem(current)
        
        self.urlList.currentItemChanged.connect(lambda current, previous: self.textEdit.setText(current.text()))

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.textEdit)
        self.layout.addWidget(self.urlList)
        self.layout.addWidget(self.button)

        #self.setWindowModality(Qt.NonModal)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Add URL Manually")
        self.setLayout(self.layout)
        self.exec_()

    def addUrl(self):
        url = self.textEdit.text()
        imagePath = url.replace('/', '') + '.png'
        self.tab.addCloseButton()
        self.tab.setTaken(url)
        self.tab.defaultTab('Loading...')
        duplicateTab = self.tab.checkDuplicateTab(url, self.tab.tabFileName)
        duplicateArchiveTab = self.tab.checkDuplicateTab(url, self.tab.archiveTabFileName)
        if duplicateTab or duplicateArchiveTab:
            if duplicateTab: self.tab.setDuplicateTab(url)
            elif duplicateArchiveTab: self.tab.setDuplicateArchiveTab(url)
            self.tab.loadSave()
        else: 
            t = threading.Thread(target=self.tab.downloadImage, args=(url, True))
            t.start()

        self.deleteLater()