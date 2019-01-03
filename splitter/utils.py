"""utils.py

Misc. functions.
"""
import os

import boto3
from flask import current_app

from splitter.exceptions import ImageFileNotFound


def get_labels_from_img(key, max_labels=10, min_confidence=90):
    """
    Return text from image using amazon rekognition.

    :param key: s3 key of image without bucket
    :type key: string
    """
    bucket = current_app.config['UPLOAD_BUCKET']
    rekognition = boto3.client("rekognition")
    response = rekognition.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        MaxLabels=max_labels,
        MinConfidence=min_confidence)
    return response['Labels']


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
    current_app.logging.warning("Deleting S3 key=%s" % key)
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
        if obj['key'] == key:
            return obj['Size']


def s3_client():
    """
    Return s3 client either for localstack (if dev) or aws .
    """
    if current_app.config['LOCALSTACK']:
        return boto3.client('s3', endpoint_url="http://localstack:4572", use_ssl=False)
    return boto3.client('s3')


def s3_resource():
    """
    Return s3 resource either for localstack (if dev) or aws .
    """
    if current_app.config['LOCALSTACK']:
        return boto3.resource('s3', endpoint_url="http://localstack:4572", use_ssl=False)
    return boto3.resource('s3')
