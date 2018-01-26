import os

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

# URL path to application (after base URL)
APP_PATH = ''

# The log file location. Set this to None if you rather want to log to stdout
# log_file_location = None
LOGFILE = os.path.join(THIS_DIR, 'log.txt')

# Path to the activation file for virtual environment
VENV_PATH = 'venv/bin/activate_this.py'

# Destination for uploaded files (absolute path)
UPLOAD_FOLDER = ''

# URL to the directory containing uploaded files
FILES_URL = ''

# Define which file extensions are allowed to be uploaded
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Generate with os.urandom(24)
SECRET_KEY = ''
