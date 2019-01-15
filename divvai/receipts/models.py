import os
import uuid
import json

from flask import current_app, flash

from splitter.database import SurrogatePK, db, Column, Model
from splitter.exceptions import S3FileNotFound
from splitter.utils import (get_text_from_img_aws, s3_keysize, upload_file_to_s3,
                            readable_filesize, get_text_from_img, delete_s3_key)


class Receipt(SurrogatePK, Model):
    __tablename__ = 'receipts'

    id = Column(db.Integer, primary_key=True)
    price = Column(db.Float, nullable=True)
    date = Column(db.DateTime, nullable=True)
    img_filename = Column(db.String, nullable=False)
    s3_key = Column(db.String, nullable=True)
    raw_text = Column(db.Text, nullable=True)
    text = Column(db.Text, nullable=True)
    is_public = Column(db.Boolean, default=True)
    restaurant_id = Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=True)

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
        base_dir = current_app.config.get('UPLOADS_DEFAULT_DEST', None)
        img_set_folder = current_app.config.get('IMAGE_SET_NAME', None)
        path = os.path.join(base_dir, img_set_folder, self.img_filename)
        if not os.path.exists(path):
            current_app.logger.warning("IMG not found locally (%s)" % path)
        return path

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

    def get_text_from_img(self, preprocess_type='threshold'):
        self.raw_text = get_text_from_img(self.img_localpath, preprocess_type)
        db.session.commit()

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
