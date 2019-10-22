# Internet Tab Holder
	
 - python3 setup.py
 - pip install -r requirements.txt
 - python3 main.py

### Build:
##### Mac:
 - pip install pyinstaller
 - pyinstaller --clean -y --windowed --onefile --name='InternetTabHolder' --add-data 'chromedriver_mac_77:.' -i resources/app.icns main.py 

 ##### Windows:
  - pip install pyinstaller
  - pyinstaller --name=InternetTabHolder --clean --onefile --noconsole --add-data chromedriver_win32_77;. -i resources\app.ico main.py
