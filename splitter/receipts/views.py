# -*- coding: utf-8 -*-
# import os
# from markupsafe import escape

from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash  # , flash_errors
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_sqlalchemy import SQLAlchemy

from splitter.database import db
from splitter.exceptions import ImageFileNotFound
from splitter.forms import UploadReceiptForm, images
from splitter.receipts.models import Receipt


blueprint = Blueprint('receipts', __name__)


@blueprint.route('/all')
def all_receipts(receipts=None):
    current_app.logger.warning('Getting all the receipts')
    if receipts is None:
        receipts = Receipt.query.all()
    return render_template('receipts/all_receipts.html', receipts=receipts)


@blueprint.route('/upload')
def add_receipt():
    # Cannot pass in 'request.form' to AddRecipeForm constructor, as this will cause 'request.files' to not be
    # sent to the form.  This will cause AddRecipeForm to not see the file data.
    # Flask-WTF handles passing form data to the form, so not parameters need to be included.
    form = UploadReceiptForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            filename = images.save(request.files['receipt_image'])
            url = images.url(filename)
            new_receipt = Receipt(filename, url)
            db.session.add(new_receipt)
            db.session.commit()
            flash('New receipt, {}, added!'.format(new_receipt.filename), 'success')
            return redirect(url_for('.all_receipts'))
        else:
            # flash(form)
            flash('ERROR! receipt was not added.', 'error')

    return render_template('receipts/upload_receipt.html', form=form)
