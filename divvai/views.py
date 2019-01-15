from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash  # , flash_errors


blueprint = Blueprint('default', __name__)


@blueprint.route('/')
def index(receipts=None):
    current_app.logger.warning('Landed at homepage.')
    return render_template('index.html')
