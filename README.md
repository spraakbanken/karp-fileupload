# Karp-Fileupload

Python 3 flask application for uploading files onto a server.

## Setup
* Install python 3 virtual environment and install its requirements:
```
pyvenv-3.4 venv
source venv/bin/activate
pip install -r requirements.txt
```
* Create directory where uploaded files are saved (needs to be accessible via URL). Make sure apache can write to this directory and the log file, e.g:
```
chmod o+w files
touch log.txt
chmod o+w log.txt
```
* Copy `config_default.py` to `config.py` and set variables inside the script.
* Create new entry in supervisord and reload, e.g:

 ```
[program:karp-fileupload]
 command=/var/www/html_sb/karp_data/karp-fileupload/venv/bin/gunicorn --chdir /var/www/html_sb/karp_data/karp-fileupload -b "0.0.0.0:5012" fileupload:create_app()
 ```
