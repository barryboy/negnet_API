# -*- coding: utf-8 -*-

from flask import Flask, g
from flask_pymongo import PyMongo
from flask_moment import Moment
from .api01 import api01
from config import config
# from .api_0_1.authentication.authentication import auth, generate_auth_token


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    mongo = PyMongo(app)
    moment = Moment(app)

    @app.before_request
    def before_request():
        g.mongo = mongo

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE')
        return response

    app.register_blueprint(api01)

    return app
