# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_DBNAME = 'negnet_dev'


class ProductionConfig(Config):
    DEBUG = False
    MONGO_DBNAME = 'negnet'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
