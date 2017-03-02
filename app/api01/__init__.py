# -*- coding: utf-8 -*-

from flask import Blueprint
api01 = Blueprint('api01', __name__)

from .routes import *
