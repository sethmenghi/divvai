"""ocr.py

Functinos relating to image recognition.
"""
import os
import tempfile

import cv2
import boto3
import imutils
import pytesseract
import numpy as np

from PIL import Image
from skimage.filters import threshold_local
from flask import current_app


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


def get_text_from_img(img_path):
    # Load image and remove color and preprocess
    image = set_image_dpi(img_path)
    # Write to local file for pytesseract to read
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, image)
    text = pytesseract.image_to_string(Image.open(filename))
    os.remove(filename)
    return text


def preprocess_img(image, preprocess_type, make_gray=True):
    """
    Return preprocessed image using techniques below.
    """
    if isinstance(image, str):
        image = cv2.imread(image)
    if preprocess_type == 'edge_detection':
        image = get_largest_rectangle(image)
        return preprocess_img(image, 'mean_threshold', False)
    if make_gray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
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


def get_largest_rectangle(image):
    ratio, resized_img = load_and_resize_img(image)
    edged = get_edges(resized_img)
    contoured_img, screenCnt = find_contours(edged, resized_img)
    warped = four_point_transform(image, screenCnt.reshape(4, 2) * ratio)
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    T = threshold_local(warped, 11, offset=10, method="gaussian")
    warped = (warped > T).astype("uint8") * 255
    return warped


def load_and_resize_img(image):
    """
    Load image, compute ratio of old height to new heigh, clone and resize.
    """
    # Speeds up processing and its more accurate
    ratio = image.shape[0] / 500.0
    resized_img = imutils.resize(image.copy(), height=500)
    return ratio, resized_img


def get_edges(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)
    return edged


def find_contours(edged, image):
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
    # loop over the contours
    screenCnt = None
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break
    if screenCnt is not None:
        cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
    else:
        raise ValueError("No appropriate contours found for image.")
    return image, screenCnt


def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # Construct points for birds eye view
    # Point order: top-left, top-right, bottom-right, bottom-left
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect
