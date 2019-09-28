import os

tabList = []
tabRows = []
tabCount = 0
loadedTabCount = 0
tabsPerRow = 3

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
ASPECT_RATIO = (float)(IMAGE_HEIGHT/IMAGE_WIDTH)
MIN_TAB_WIDTH = 360
MIN_TAB_HEIGHT = (int)(MIN_TAB_WIDTH*ASPECT_RATIO)

ABSOLUTE_IMAGE_FOLDER_PATH = os.path.join(os.getcwd(), 'thumbnails')
IMAGE_FOLDER_PATH = 'thumbnails'