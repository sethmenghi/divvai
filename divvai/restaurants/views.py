# -*- coding: utf-8 -*-
# import os
# from markupsafe import escape

from flask import Blueprint

from divvai.restaurants.models import Restaurant


blueprint = Blueprint('restaurants', __name__)
