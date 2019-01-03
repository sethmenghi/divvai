import os


class DefaultConfig(object):
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')
    LOG_DIR = '.'  # create log files in current working directory
    PROJECT_NAME = 'splitter'
    LOGGING_LEVEL = 'info'
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    # Flask-Uploads config
    UPLOADED_FILES_ALLOW = set(['png', 'jpg', 'jpeg', 'gif'])
    UPLOADED_FILES_URL = '/app/uploads/'
    UPLOADS_DEFAULT_DEST = '/app/uploaded_sets'
    UPLOAD_BUCKET = os.environ.get('UPLOAD_BUCKET', 'splitter')
    # POSTGRES Database Conf
    DB_USER = os.environ.get('POSTGRES_USER', 'splitter')
    DB_PASS = os.environ.get('POSTGRES_PASSWORD', 'splitter')
    DB_HOST = os.environ.get('POSTGRES_HOST', 'splitterpg_dev')
    DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
    DB_NAME = os.environ.get('POSTGRES_DB', 'splitter')
    DEFAULT_DB = 'postgresql://{}:{}@{}:{}/{}'.format(
        DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', DEFAULT_DB)


class ProductionConfig(DefaultConfig):
    pass


class TestConfig(DefaultConfig):
    TESTING = True


class DevConfig(DefaultConfig):
    BOOTSTRAP_SERVE_LOCAL = True
    SERVER_NAME = '0.0.0.0'
    FLASK_DEBUG = True
    LOCALSTACK = True


configs = {
    'test': TestConfig,
    'dev': DevConfig,
    'prod': ProductionConfig,
    'default': DefaultConfig
}
