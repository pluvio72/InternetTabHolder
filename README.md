# Internet Tab Holder
	
 - python setup.py
 - pip install -r requirements.txt
 - python3 main.py

### Build:
 - pip install pyinstaller
 - pyinstaller --clean -y --windowed --onefile --name='InternetTabHolder' --add-data 'chromedriver_mac_77:.' -i resources/app.icns main.py 
