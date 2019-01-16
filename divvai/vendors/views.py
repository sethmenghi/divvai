# -*- coding: utf-8 -*-
# import os
# from markupsafe import escape

from flask import Blueprint

from divvai.vendors.models import Vendor


blueprint = Blueprint('vendors', __name__)
