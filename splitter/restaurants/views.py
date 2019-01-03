# -*- coding: utf-8 -*-
# import os
# from markupsafe import escape

from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash  # , flash_errors
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_sqlalchemy import SQLAlchemy

from splitter.database import db
from splitter.exceptions import ImageFileNotFound
from splitter.forms import UploadreceiptForm, images
from splitter.models import receipt


blueprint = Blueprint('restaurants', __name__)
