from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from splitter.extensions import images


class UploadReceiptForm(FlaskForm):
    receipt_image = FileField(
        'Receipt Image',
        validators=[
            FileRequired(),
            FileAllowed(images, 'Images only!')
        ]
    )
