import os
import uuid

from flask import current_app

from splitter.database import SurrogatePK, db, Column, Model
from splitter.exceptions import ImageFileNotFound
from splitter.utils import get_labels_from_img, s3_keysize, upload_file_to_s3, delete_s3_key


class receipt(SurrogatePK, Model):
    __tablename__ = 'receipts'

    id = Column(db.Integer, primary_key=True)
    price = Column(db.Float, nullable=False)
    date = Column(db.DateTime, nullable=True)
    img_filename = Column(db.String, nullable=False)
    s3_key = Column(db.String, default=None, nullable=True)
    labels = Column(db.Text, default=None, nullable=True)
    is_public = Column(db.Boolean, default=True)
    restaurant_id = db.relationship('Restaurant', backref='receipt', lazy=True)

    def __init__(self, img_filename, url):
        """
        Initialize the receipt object by processing the image.
        """
        # self.date = date
        # self.price = price
        self.img_filename = img_filename
        self.url = url
        # self.json_str = json_str
        # self.restaurant_id = restaurant_id
        file_ext = os.path.split(img_filename)[1]
        self.s3_key = str(uuid.uuid1()) + file_ext
        self.upload_img_to_s3()
        self.process_img()

    def __repr__(self):
        return '<id: {}, price: {}, date: {}'.format(self.id, self.price, self.date)

    @property
    def in_s3(self):
        """
        Return True if in s3.
        """
        return self.img_size_s3 is not None

    @property
    def img_size(self):
        """
        Return size of img.
        """
        if os.path.exists(self.img_filename):
            return os.path.getsize(self.img_filename)
        e = "Local receipt img not found: %s" % self.img_filename
        current_app.logger.warning("File not found locally or in S3.")
        raise ImageFileNotFound(e)

    @property
    def img_size_s3(self):
        """
        Return size of img as in s3.
        """
        return s3_keysize(self.s3_key)

    @property
    def img_obj(self):
        # Get img if local, or get img if on s3
        pass

    def safe_s3_upload(self):
        """
        Upload img to s3 if it doesn't exist or the size doesn't match.
        """
        s3_size = self.img_size_s3
        if s3_size != self.img_size:
            log = "Local img size doesn't match size in S3 - Deleting and reuploading"
            current_app.logging.warning(log)
            delete_s3_key(self.s3_key)
            s3_size = None
        if s3_size is None:
            self.upload_img_to_s3()

    def upload_img_to_s3(self):
        """
        Upload img to S3.
        """
        upload_file_to_s3(self.img_filename, self.s3_key)

    def process_img(self):
        """
        Set JSON values.
        """
        self.labels = get_labels_from_img(self.s3_key)