import os

# The log folder location
LOG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logs")

# Set log level to debug
DEBUG = False

# Destination for uploaded files (absolute path)
UPLOAD_FOLDER = ""

# URL to the directory containing uploaded files
FILES_URL = ""

# Define which file extensions are allowed to be uploaded
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])

# Generate with os.urandom(24)
SECRET_KEY = ""

# Needed if application is not mounted in root
APPLICATION_ROOT = ""
