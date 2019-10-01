import os

TABS_FILE_NAME = 'tabs_1.txt'
ARCHIVED_TABS_FILE_NAME = '.tabs_1.txt'

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
ASPECT_RATIO = (float)(IMAGE_HEIGHT/IMAGE_WIDTH)
MIN_TAB_WIDTH = 360
MIN_TAB_HEIGHT = (int)(MIN_TAB_WIDTH*ASPECT_RATIO)

ABSOLUTE_IMAGE_FOLDER_PATH = os.path.join(os.getcwd(), 'thumbnails')
IMAGE_FOLDER_PATH = 'thumbnails'

def tabFileName(pageNumber):
    return 'tabs_' + str(pageNumber) + '.txt'

def archiveTabFileName(pageNumber):
    return '.tabs_' + str(pageNumber) + '.txt'

class TabSettings():
    def __init__(self):
        self.tabList = []
        self.emptyTab = None
        self.tabRows = []
        self.tabCount = 0
        self.loadedTabCount = 1
        self.tabsPerRow = 3