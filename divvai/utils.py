"""utils.py

Misc. functions.
"""
import os

import boto3
from flask import current_app

from divvai.exceptions import ImageFileNotFound, S3FileNotFound


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
