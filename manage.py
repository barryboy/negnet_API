#!/usr/bin/env python

import os
from app import create_app

app = create_app(os.getenv('NEGNET_CONFIG') or 'default')

if __name__ == "__main__":
    app.run()
