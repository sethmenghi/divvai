import os
import uuid
import json
import cv2
import tempfile

from werkzeug.datastructures import FileStorage

from flask import current_app, flash

from divvai import process
from divvai.database import SurrogatePK, db, Column, Model
from divvai.exceptions import S3FileNotFound
from divvai.extensions import images
from divvai.ocr import (get_text_from_img_aws, get_text_from_img, preprocess_img)
from divvai.utils import (s3_keysize, upload_file_to_s3, get_upload_file,
                          readable_filesize, delete_s3_key)


class Receipt(SurrogatePK, Model):
    __tablename__ = 'receipts'

    id = Column(db.Integer, primary_key=True)
    img_filename = Column(db.String, nullable=False)
    preprocessed_img_filename = Column(db.String, nullable=True)
    s3_key = Column(db.String, nullable=True)
    raw_text = Column(db.Text, nullable=True)
    text = Column(db.Text, nullable=True)
    is_public = Column(db.Boolean, default=True)
    vendor_id = Column(db.Integer, db.ForeignKey('vendors.id'), nullable=True)

    def __init__(self, img_filename, url):
        """
        Initialize the receipt object by processing the image.
        """
        self.img_filename = img_filename
        self.url = url

    def __repr__(self):
        return '<id: {}, price: {}, date: {}'.format(self.id, self.price, self.date)

    @property
    def img_localpath(self):
        return get_upload_file(self.img_filename)

    @property
    def preprocessed_img_localpath(self):
        return get_upload_file(self.preprocessed_img_filename)

    @property
    def in_s3(self):
        """
        Return True if in s3.
        """
        if self.s3_key is None:
            return False
        try:
            self.img_size_s3
            return True
        except S3FileNotFound:
            return False

    @property
    def img_size(self):
        """
        Return size of img.
        """
        if os.path.exists(self.img_localpath):
            return os.path.getsize(self.img_localpath)
        flash("img not found: %s" % self.img_localpath, 'error')
        return 0

    @property
    def readable_img_size(self):
        return readable_filesize(self.img_size)

    @property
    def img_size_s3(self):
        """
        Return size of img as in s3.
        """
        if self.s3_key:
            return s3_keysize(self.s3_key)

    @property
    def img_obj(self):
        """
        Get img obj.
        """
        with open(self.img_localpath, 'rb') as f:
            return f.read()

    @property
    def phone_num(self):
        if self.raw_text:
            return process.get_phone(self.raw_text)

    @property
    def email(self):
        if self.raw_text:
            return process.get_email(self.raw_text)

    @property
    def address(self):
        if self.raw_text:
            return process.get_street(self.raw_text)

    @property
    def date(self):
        return None

    @property
    def price(self):
        return None

    def save_preprocessed_img(self, preprocess_type):
        if self.preprocessed_img_filename and os.path.exists(self.preprocessed_img_localpath):
            msg = "Deleting Preprocessed Image: %s" % self.preprocessed_img_filename
            current_app.logger.warning(msg)
            os.remove(self.preprocessed_img_localpath)
        img = preprocess_img(self.img_localpath, preprocess_type)
        with tempfile.NamedTemporaryFile(delete=True, prefix='preprocessed', suffix='.jpg') as tmp_fh:
            cv2.imwrite(tmp_fh.name, img)
            self.preprocessed_img_filename = images.save(FileStorage(tmp_fh, filename=tmp_fh.name))
        db.session.commit()

    def get_text_from_img(self):
        if self.preprocessed_img_filename:
            self.raw_text = get_text_from_img(self.preprocessed_img_localpath)
        else:
            self.raw_text = get_text_from_img(self.img_localpath)
        db.session.commit()

    def safe_s3_upload(self):
        """
        Upload img to s3 if it doesn't exist or the size doesn't match.
        """
        if self.s3_key is None:
            self.set_s3_key()
            self.upload_img_to_s3()
        elif not self.in_s3:
            self.upload_img_to_s3()
        elif self.img_size_s3 != self.img_size:
            e = "Local img size doesn't match S3. Receipt=%s" % self.id
            current_app.logger.error(e)
            raise ValueError(e)
        elif self.img_size_s3:
            current_app.logger.info("Not loading to S3. File already exists.")
        else:
            self.upload_img_to_s3()
            current_app.logger.info("S3 file (%s) uploaded." % self.s3_key)

    def upload_img_to_s3(self):
        """
        Upload img to S3.
        """
        upload_file_to_s3(self.img_localpath, self.s3_key)

    def set_s3_key(self):
        """
        Set s3_key if None.
        """
        if self.s3_key is None:
            file_ext = os.path.split(self.img_filename)[1].split('.')[-1]
            self.s3_key = str(uuid.uuid1()) + '.' + file_ext
            db.session.commit()

    def delete_s3_key(self):
        """
        Delete S3 key.
        """
        if self.in_s3:
            delete_s3_key(self.s3_key)

    def safe_get_text_from_img_aws(self):
        """
        Safely get text from img.
        """
        # Images larger than 5 MB need to be in S3.
        if self.img_size >= 1048576:
            self.set_s3_key()
            self.safe_s3_upload()
            self.get_text_from_img()
        else:
            self.get_text_from_img(img_bytes=self.img_obj)

    def get_text_from_img_aws(self, img_bytes=None):
        """
        Set JSON values.
        """
        if not img_bytes:
            text = get_text_from_img_aws(key=self.s3_key)
        else:
            text = get_text_from_img_aws(img_bytes=img_bytes)
        current_app.logger.info("Retrieved text: %s" % text)
        self.raw_text = json.dumps(text)
        db.session.commit()
