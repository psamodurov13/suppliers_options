# Suppliers options

The program performs the functions:
- parsing images for individual product variations (3 suppliers)
- comparison of related products (1 supplier)
- preparation of the export/import file for uploading to the site (for OpenCart)

## INSTALLING THE PROGRAM ON A NEW SITE (Shared hosting Timeweb)

- Create folder 123/public_html/parse_suppliers
- Upload the archive to 123/public_html/parse_suppliers
- Unpack the archive
- Editing auth_data.py (paths to the folder with the program, path to the site, downloadable providers)
- Create a folder "options_img" in the directory "/123/public_html/image/catalog"
- Connect via SSH. Through the terminal or SSH console in the hosting
  - ssh cy******@IP-adress
- install virtual environment
  - go to our folder (cd 123/public_html/parse_suppliers)
  - download virtualenv (wget https://bootstrap.pypa.io/virtualenv/3.6/virtualenv.pyz)
  - create a virtual environment (python3 virtualenv.pyz venv)
  - activate virtual environment, /c/ - first letter of login, /cy******/ - login (source /home/c/cy******/123/public_html/parse_suppliers/venv/bin/activate)
  - install all required packages (pip install -r requirements.txt)
  - change permissions for webdriver (chmod 755 phantomjs-2.1.1-linux-x86_64/bin/phantomjs)


## STARTING AN ALREADY INSTALLED PROGRAM
- Connect via SSH. Through the terminal or SSH console in the hosting
  - ssh cy******@IP-adress
  - go to our folder (cd 123/public_html/parse_suppliers)
  - activate virtual environment, /c/ - first letter of login, /cy******/ - login (source /home/c/ca******/123/public_html/parse_suppliers/venv/bin/activate)
- download files of unloading options and products from the impotr/export tool
- upload them to 123/public_html/parse_suppliers
- run the file (python3 main.py)
- download ready-made files from 123/public_html/parse_suppliers
- upload files to the impotr/export tool
