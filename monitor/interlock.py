import numpy as np
import matplotlib.pyplot as plt

from birdseye import BirdsEye
from helpers import roi
from lanefilter import LaneFilter
from conformance import conformance_test
from geometric import geometric_test

def get_binary(img, birds_eye, thresholds):
    """
    Applies transformations to process the given image
    :param img: the given image
    :param birds_eye: the bird's eye transformation object
    :param thresholds: thresholds used for vision filters
    :return: the processed image
    """
    lane_filter = LaneFilter(thresholds)
    binary = lane_filter.apply(img)
    birds_eye_view = birds_eye.sky_view(binary)
    width = birds_eye_view.shape[1]
    return roi(birds_eye_view, width//10, width - width//10).astype(np.uint8)

def run_tests(certificate):
    img = certificate['img']
    left_line = certificate['left']
    right_line = certificate['right']
    birds_eye = BirdsEye(certificate['source'], certificate['dest'])
    wb = get_binary(img, birds_eye, certificate['thresholds'])
    shape_result = geometric_test(left_line, right_line, img.shape[0])
    left_result = conformance_test(True, left_line, wb)
    right_result = conformance_test(False, right_line, wb)
    result = birds_eye.project(img, wb, left_line, right_line)
    return shape_result, left_result, right_result
