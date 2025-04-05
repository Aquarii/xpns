import os

basedir = os.path.abspath(os.path.dirname(__name__))


class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY', 'MONAMONA')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = 8035200
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite+pysqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    REMEMBER_COOKIE_DURATION = 60

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite+pysqlite://'
    REMEMBER_COOKIE_DURATION = 180


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite+pysqlite:///' + os.path.join(basedir, 'data.sqlite')
    REMEMBER_COOKIE_DURATION = 2678400

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    
    'default': DevelopmentConfig
}