from flask_wtf import FlaskForm
from wtforms import SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired

from divvai.extensions import images


class UploadReceiptForm(FlaskForm):
    receipt_image = FileField(
        'Receipt Image',
        validators=[
            FileRequired(),
            FileAllowed(images, 'Images only!')
        ]
    )


class ProcessReceiptForm(FlaskForm):
    """
    Form for processing a receipt using different opencv2 methods.
    """
    preprocess_type = SelectField('Preprocess Method', choices=[
        ('median_blur', 'Median Blur'),
        ('bilateral_filter', 'Bilateral Filter'),
        ('threshold', 'Threshold'),
        ('mean_threshold', 'Adaptive Mean Thresholding'),
        ('gauss_threhold', 'Adaptive Gaussian Thresholding')
    ], default='threshold')
