# Karp-Fileupload

Python 3 flask application for uploading files onto a server.

## Setup
* Install python 3 virtual environment and install its requirements:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
* Create directory where uploaded files are saved (needs to be accessible via URL).
* Copy `config_default.py` to `config.py` and set variables inside the script.
* Create new entry in supervisord and reload, e.g:

 ```
[program:karp-fileupload]
 command=/var/www/html_sb/karp_data/skbl/venv/bin/gunicorn --chdir /var/www/html_sb/karp_data/skbl -b "0.0.0.0:5012" fileupload:create_app()
 ```
