import subprocess
import requests
import getpass
import zipfile
import shutil
import sys
import os

macdriver_url = 'https://chromedriver.storage.googleapis.com/77.0.3865.40/chromedriver_mac64.zip'
windriver_url = 'https://chromedriver.storage.googleapis.com/77.0.3865.40/chromedriver_win32.zip'

platform = sys.platform

if platform == 'darwin' or platform == 'win32':
    mac = True if platform == 'darwin' else False
    chosen_url = macdriver_url if mac else windriver_url
    file_name = 'chromedriver_mac_77' if mac else 'chromedriver_win32_77'
    with requests.get(chosen_url, stream=True) as download_stream:
        with open('zip_file.zip', 'wb') as file_stream:
            shutil.copyfileobj(download_stream.raw, file_stream)
    
    with zipfile.ZipFile('zip_file.zip', 'r') as z:
        z.extractall('./')

    if platform == 'win32':
        user = getpass.getuser()
        os.system('del zip_file.zip')
        os.system('mv chromedriver.exe ' + file_name)
        os.system('icacls ' + file_name + ' /grant ' + user + ':(rx)')
    elif platform == 'darwin':
        os.system('rm zip_file.zip && mv chromedriver ' + file_name)
        os.system('chmod +x ' + file_name)
else:
    print('Platform not supported:::')
    sys.exit(0)