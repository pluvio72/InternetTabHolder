import os

WINDOW_NAME = 'Internet Tab Holder '

TABS_FILE_NAME = 'tabs_1.txt'
ARCHIVED_TABS_FILE_NAME = '.tabs_1.txt'

ARCHIVE_TAB_FILE_MAX_SIZE = 100

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
ASPECT_RATIO = (float)(IMAGE_HEIGHT/IMAGE_WIDTH)
MIN_TAB_WIDTH = 360
MIN_TAB_HEIGHT = (int)(MIN_TAB_WIDTH*ASPECT_RATIO)

IMAGE_FOLDER_PATH = 'thumbnails'

def absImageFolderPath():
    return os.path.join(os.getcwd(), 'thumbnails')

def tabFileName(tab):
    return str(tab.pageNumber) + '.txt'

def archiveTabFileName(tab):
    return '.' + str(tab.pageNumber) + '.txt'

class TabSettings():
    def __init__(self):
        self.tabList = []
        self.emptyTab = None
        self.tabRows = []
        self.tabCount = 0
        self.loadedTabCount = 1
        self.tabsPerRow = 3