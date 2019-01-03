from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES


images = UploadSet('images', IMAGES)


class UploadReceiptForm(Form):
    receipt_image = FileField(
        'receipt Image',
        validators=[
            FileRequired(),
            FileAllowed(images, 'Images only!')
        ]
    )
