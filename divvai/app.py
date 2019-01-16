# -*- coding: utf-8 -*-
import os

from flask import Flask

# from flask_nav import Nav
from flask_uploads import configure_uploads

from divvai import receipts, vendors
from divvai import views
from divvai.extensions import bcrypt, db, migrate, bootstrap, images
from divvai.settings import configs


def create_app(config=None):
    app = Flask(__name__.split('.')[0])

    config = os.environ.get('CONFIG', 'dev')
    app.logger.info("Config: %s" % config)
    app.config.from_object(configs.get(config, None) or configs['default'])
    app.template_folder = app.config.get('TEMPLATE_FOLDER', 'templates')

    register_extensions(app)
    register_blueprints(app)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    configure_uploads(app, images)


def register_blueprints(app):
    """Register Flask blueprints."""
    # origins = app.config.get('CORS_ORIGIN_WHITELIST', '*')
    # cors.init_app(receipts.views.blueprint, origins=origins)
    # cors.init_app(vendors.views.blueprint, origins=origins)
    app.register_blueprint(views.blueprint, url_prefix='/')
    app.register_blueprint(receipts.views.blueprint, url_prefix='/receipts')
    app.register_blueprint(vendors.views.blueprint, url_prefix='/vendors')
