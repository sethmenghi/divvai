# -*- coding: utf-8 -*-
import os

from flask import Flask

# from flask_nav import Nav
from flask_uploads import UploadSet, IMAGES, configure_uploads

from splitter import receipts, restaurants
from splitter.extensions import bcrypt, db, migrate, conf, bootstrap
from splitter.settings import configs


def create_app(config=None):
    app = Flask(__name__.split('.')[0])

    config = os.environ.get('CONFIG', 'dev')
    app.logger.info("Config: %s" % config)
    app.config.from_object(configs.get(config, None) or configs['default'])

    register_extensions(app)
    register_blueprints(app)

    images = UploadSet('images', IMAGES)
    configure_uploads(app, images)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    conf.init_app(app)
    bootstrap.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    # origins = app.config.get('CORS_ORIGIN_WHITELIST', '*')
    # cors.init_app(receipts.views.blueprint, origins=origins)
    # cors.init_app(restaurants.views.blueprint, origins=origins)

    app.register_blueprint(receipts.views.blueprint)
    app.register_blueprint(restaurants.views.blueprint)
