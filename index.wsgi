import sys
import logging
import os

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
if THIS_DIR not in sys.path:
    sys.path.append(THIS_DIR)

import config

logging.basicConfig(filename=config.LOGFILE, format="%(asctime)-15s %(message)s")
log = logging.getLogger('fileupload')
log.setLevel(logging.INFO)
# log.info("Restarted index.wsgi")

# Activate virtual environment
activate_this = os.path.join(THIS_DIR, config.VENV_PATH)
execfile(activate_this, dict(__file__=activate_this))

from fileupload import app as real_app


def application(env, resp):
    env['SCRIPT_NAME'] = config.APP_PATH
    return real_app(env, resp)


# if __name__ == '__main__':
#     run_simple('localhost', 5000, app,
#                use_reloader=True, use_debugger=True, use_evalex=True)
