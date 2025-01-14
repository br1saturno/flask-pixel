# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    # SECRET_KEY = config('SECRET_KEY'  , default='S#perS3crEt_007')
    SECRET_KEY = os.getenv('SECRET_KEY', 'S#perS3crEt_007')

    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')    
    
class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://br1:vacabutterfly@localhost:5432/hues-generated'.format(
        os.getenv('DB_ENGINE'   , 'mysql'),
        os.getenv('DB_USERNAME' , 'br1'),
        os.getenv('DB_PASS'     , 'vacabutterfly'),
        os.getenv('DB_HOST'     , 'localhost'),
        os.getenv('DB_PORT'     , 5432),
        os.getenv('DB_NAME'     , 'hues-generated')
    )

    # SQLALCHEMY_DATABASE_URI = 'postgresql://hues-generated:AVNS_BulNeWAQz86gTToiC9K@app-ad45a6f8-50b3-4ca1-aa0d-5be49f192c73-do-user-12868344-0.b.db.ondigitalocean.com:25060/hues-generated'.format(
    #     os.getenv('DB_ENGINE'   , 'mysql'),
    #     os.getenv('DB_USERNAME' , 'hues-generated'),
    #     os.getenv('DB_PASS'     , 'AVNS_BulNeWAQz86gTToiC9K'),
    #     os.getenv('DB_HOST'     , 'app-ad45a6f8-50b3-4ca1-aa0d-5be49f192c73-do-user-12868344-0.b.db.ondigitalocean.com'),
    #     os.getenv('DB_PORT'     , 25060),
    #     os.getenv('DB_NAME'     , 'hues-generated'),
    #     os.getenv('DB_SSLMODE'  , 'require')
    # )
    #
    # ssl_mode = "?sslmode=require"
    # SQLALCHEMY_DATABASE_URI += ssl_mode


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
