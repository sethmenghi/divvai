import os


class DefaultConfig(object):
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')
    LOG_DIR = '.'  # create log files in current working directory
    PROJECT_NAME = 'splitter'
    LOGGING_LEVEL = 'info'
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    # POSTGRES Database Conf
    DB_USER = os.environ.get('POSTGRES_USER', 'splitter')
    DB_PASS = os.environ.get('POSTGRES_PASSWORD', 'splitter')
    DB_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
    DB_NAME = os.environ.get('POSTGRES_DB', 'splitter')
    DEFAULT_DB = 'postgresql://{}:{}@{}:{}/{}'.format(
        DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', DEFAULT_DB)

    # Flask-Uploads config
    UPLOADED_FILES_ALLOW = set(['png', 'jpg', 'jpeg', 'gif'])
    UPLOADS_DEFAULT_DEST = os.path.join(APP_DIR, 'uploads')
    UPLOAD_BUCKET = os.environ.get('UPLOAD_BUCKET', 'receipt-splitter')
    IMAGE_SET_NAME = 'images'
    UPLOAD_IMAGE_DIR = os.path.join(UPLOADS_DEFAULT_DEST, IMAGE_SET_NAME)
    # UPLOADED_FILES_URL = os.path.join(APP_DIR, 'uploads/')

    TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')


class ProductionConfig(DefaultConfig):
    pass


class TestConfig(DefaultConfig):
    TESTING = True


class DevConfig(DefaultConfig):
    BOOTSTRAP_SERVE_LOCAL = True
    FLASK_DEBUG = True
    LOCALSTACK = False
    LOGGING_LEVEL = 'debug'


configs = {
    'test': TestConfig,
    'dev': DevConfig,
    'prod': ProductionConfig,
    'default': DefaultConfig
}
