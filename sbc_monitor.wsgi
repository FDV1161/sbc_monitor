#! /var/www/sbc_monitor/venv/bin/python3
project_folder = '/var/www/sbc_monitor'

activate_this = project_folder + '/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, project_folder)
from sbc import app as application
application.secret_key = 'anythingsecretkey'

