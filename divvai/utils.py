"""utils.py

Misc. functions.
"""
import os
import tempfile

import boto3
import pytesseract
import cv2
from flask import current_app
from PIL import Image

from splitter.exceptions import ImageFileNotFound, S3FileNotFound


def get_text_from_img(img_path, preprocess_type='threshold'):
    # Load image and remove color and preprocess
    image = set_image_dpi(img_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    preprocessed_img = preprocess_img(gray, preprocess_type)
    # Write to local file for pytesseract to read
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, preprocessed_img)
    text = pytesseract.image_to_string(Image.open(filename))
    os.remove(filename)
    return text


def preprocess_img(gray, preprocess_type):
    """
    Return preprocessed image using techniques below.
    """
    if preprocess_type == 'median_blur':
        return cv2.medianBlur(gray, 3)
    elif preprocess_type == 'bilateral_filter':
        return cv2.bilateralFilter(gray, 9, 10, 200)
    elif preprocess_type == 'threshold':
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    elif preprocess_type == 'mean_threshold':
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY, 11, 2)
    elif preprocess_type == 'gauss_threshold':
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 11, 2)
    raise ValueError("Preprocess Method (%s) not recognized.")


def set_image_dpi(file_path):
    """
    Return opencv2 image from file_path with a DPI of 300. Optimized for pytesseract.
    """
    im = Image.open(file_path)
    length_x, width_y = im.size
    factor = min(1, float(1024.0 / length_x))
    size = int(factor * length_x), int(factor * width_y)
    im_resized = im.resize(size, Image.ANTIALIAS)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    temp_filename = temp_file.name
    im_resized.save(temp_filename, dpi=(300, 300))
    return cv2.imread(temp_filename)


def get_text_from_img_aws(key=None, img_bytes=None):
    """
    Return text from image using amazon rekognition.

    :param key: s3 key of image without bucket
    :type key: string
    :param img_bytes: Blob of img to use rekognition
    :type img_bytes: bytes
    """
    rekognition = boto3.client("rekognition")
    if key:
        bucket = current_app.config['UPLOAD_BUCKET']
        response = rekognition.detect_text(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            })
    elif img_bytes:
        response = rekognition.detect_text(Image={'Bytes': img_bytes})
    else:
        e = "One of these parameters must be set: (key, img_bytes)"
        raise ValueError(e)
    return response


def raise_error_if_file_doesnt_exist(image_path):
    """
    Raise exception if file not found.
    """
    if os.path.exists(image_path):
        e = "Local image file not found: %s" % image_path
        raise ImageFileNotFound(e)


def upload_file_to_s3(path, key):
    """
    Upload file to s3.
    """
    current_app.logger.debug("Loading local file to S3: %s)" % key)
    s3 = s3_client()
    bucket = current_app.config['UPLOAD_BUCKET']
    s3.upload_file(path, bucket, key)


def delete_s3_key(key):
    """
    Delete s3 key if exists.
    """
    s3 = s3_resource()
    current_app.logger.warning("Deleting S3 key=%s" % key)
    bucket = current_app.config['UPLOAD_BUCKET']
    s3.Object(bucket, key).delete()


def s3_keysize(key):
    """
    Return size of file in s3.
    """
    s3 = s3_client()
    bucket = current_app.config['UPLOAD_BUCKET']
    response = s3.list_objects_v2(Bucket=bucket, Prefix=key)
    for obj in response.get('Contents', []):
        if obj['Key'] == key:
            return obj['Size']
    raise S3FileNotFound("S3 Key %s doesn't exist." % key)


def s3_client():
    """
    Return s3 client either for localstack (if dev) or aws .
    """
    if current_app.config['LOCALSTACK']:
        localstack_host = current_app['S3_LOCALSTACK_HOST']
        return boto3.client('s3', endpoint_url=localstack_host, use_ssl=False)
    return boto3.client('s3')


def s3_resource():
    """
    Return s3 resource either for localstack (if dev) or aws .
    """
    if current_app.config['LOCALSTACK']:
        localstack_host = current_app['S3_LOCALSTACK_HOST']
        return boto3.resource('s3', endpoint_url=localstack_host, use_ssl=False)
    return boto3.resource('s3')


def readable_filesize(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)
