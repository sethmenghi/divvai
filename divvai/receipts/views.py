# -*- coding: utf-8 -*-
import os

from flask import (Blueprint, render_template, redirect, url_for,
                   request, current_app, flash, send_from_directory)

from divvai.database import db
from divvai.forms import UploadReceiptForm, ProcessReceiptForm
from divvai.receipts.models import Receipt
from divvai.extensions import images


blueprint = Blueprint('receipts', __name__)


@blueprint.route('/upload', methods=['GET', 'POST'])
def upload_receipt():
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
            msg = "New receipt, {}, added!".format(new_receipt.img_filename)
            current_app.logger.info(msg)
            flash(msg, 'success')
            return redirect(url_for('.receipt_detail', receipt_id=new_receipt.id))
        else:
            flash('ERROR! receipt was not added.', 'error')

    return render_template('receipts/upload_receipt.html', form=form)


@blueprint.route('/all')
def all_receipts(receipts=None):
    """
    Display all receipts in db.
    """
    current_app.logger.warning('Getting all the receipts')
    if receipts is None:
        receipts = Receipt.query.all()
    return render_template('receipts/all_receipts.html', receipts=receipts)


@blueprint.route('/<receipt_id>', methods=['GET', 'POST'])
def receipt_detail(receipt_id):
    """
    Show receipt details, including a modal/form for processing.
    """
    receipt = Receipt.query.get(receipt_id)
    form = ProcessReceiptForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            return redirect(url_for('.process_receipt', receipt_id=receipt_id,
                                    preprocess_type=form.preprocess_type.data))
        else:
            flash('Form validation failed for form.', 'error')
    return render_template('receipts/receipt_detail.html', receipt=receipt, form=form)


@blueprint.route("/<receipt_id>/api/process/<preprocess_type>")
def process_receipt(receipt_id, preprocess_type='edge_detection'):
    """
    """
    receipt = Receipt.query.get(receipt_id)
    if receipt.raw_text:
        flash("Text for %s reprocessed" % receipt.img_filename, 'warning')
    else:
        flash("Text for %s processed" % receipt.img_filename)
    receipt.get_text_from_img(preprocess_type)
    return redirect(url_for('.receipt_detail', receipt_id=receipt_id))


@blueprint.route("/<receipt_id>/api/delete")
def delete_receipt(receipt_id):
    """
    Delete receipt from db and delete local img.
    """
    receipt = Receipt.query.get(receipt_id)
    if os.path.exists(receipt.img_localpath):
        os.remove(receipt.img_localpath)
        current_app.logger.warning("Deleted local img: %s" % receipt.img_localpath)
    if receipt.s3_key:
        receipt.delete_s3_key()
    db.session.delete(receipt)
    db.session.commit()
    flash("Deleted %s" % receipt.img_filename)
    return redirect(url_for('.all_receipts'))


@blueprint.route("/<receipt_id>/api/img/<_type>")
def img_link(receipt_id, _type):
    receipt = Receipt.query.get(receipt_id)
    upload_folder = current_app.config.get('UPLOAD_IMAGE_DIR')
    if _type == 'base':
        return send_from_directory(upload_folder, receipt.img_filename)
    elif _type == 'cropped':
        return send_from_directory(upload_folder, receipt.cropped_img)
    else:
        raise TypeError("Recieved invalid _type parameter: %s" % _type)


@blueprint.route("/<receipt_id>/api/s3")
def put_img_s3(receipt_id):
    """
    Upload the image to S3.
    """
    receipt = Receipt.query.get(receipt_id)
    if receipt.in_s3:
        flash("Receipt[%s] is already in S3." % receipt_id)
    else:
        receipt.safe_s3_upload()
        flash("Receipt[%s] uploaded to s3." % receipt_id)
    return redirect(url_for('.receipt_detail', receipt_id=receipt_id))
