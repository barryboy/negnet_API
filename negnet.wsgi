#!/usr/bin/python
import os
import sys
from app import create_app
activate_this = '/home/negnet/.virtualenvs/negnet/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
sys.stdout = sys.stderr
sys.path.insert(0, "/home/negnet/API/")

application = create_app(os.getenv('NEGNET_CONFIG') or 'default')
