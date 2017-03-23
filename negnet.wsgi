#!/usr/bin/python
activate_this = '/home/negnet/.virtualenvs/negnet/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
import os
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/negnet/")

from API.app import create_app
application = create_app(os.getenv('NEGNET_CONFIG') or 'default')
