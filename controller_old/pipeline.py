import matplotlib.pyplot as plt
import cv2
import numpy as np
import pickle
import socketserver
import socket
import os

from birdseye import BirdsEye
from lanefilter import LaneFilter
from curves import Curves
from helpers import roi
import sys
from scipy import signal
import random

if os.environ.get('PROD'):
    HOST = '172.168.1.130' 
else:
    HOST = '127.0.1.1'


SENSOR_PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
MONITOR_PORT = 54321

old_certificate = None

# np.set_printoptions(threshold=sys.maxsize)
SCALE_FACTOR = 1/10
X_CROP = 150
SOURCE_PTS = [(430, 100), (55, 360), (960, 360), (553, 100)]
DEST_PTS = [(170, -360), (170, 360), (810, 360), (810, -360)]
REG_THRESHOLDS = { 'sat_thresh': 120, 'light_thresh': 40, 'light_thresh_agr': 205,
              'grad_thresh': (0.7, 1.4), 'mag_thresh': 40, 'x_thresh': 20 }

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

def resize(lines, source_pts, dest_pts, scale_factor):
    """
    resizes parameters to reduce the size of the certificate
    """
    for line in lines:
        line[0] /= scale_factor
        line[2] = (line[2]) * scale_factor
    source_pts = [(pt[0] * scale_factor, pt[1] * scale_factor) for pt in source_pts]
    dest_pts = [(pt[0] * scale_factor, pt[1] * scale_factor) for pt in dest_pts]
    return lines[0], lines[1], source_pts, dest_pts

def get_certificate(img, low_res, time_stamp, signature):
    """
    Finds the lane lines in the given image
    :param img: the image to find the lane lines on
    :param birds_eye: the bird's eye transformation object
    :param thresholds: thresholds used for vision filters
    :return: the coefficients of the detected left and right lane lines as 2nd degree polynomials
    """
    global old_certificate
    if old_certificate is not None:
        return old_certificate
    birds_eye = BirdsEye(SOURCE_PTS, DEST_PTS)
    wb = get_binary(img, birds_eye, REG_THRESHOLDS)
    curves = Curves(number_of_windows=9, margin=100, minimum_pixels=10,
                    ym_per_pix=30 / 720, xm_per_pix=3.7 / 700)
    result = curves.fit(wb)
    # print(result)
    visual = birds_eye.project(img, wb, result['pixel_left_best_fit_curve'], result['pixel_right_best_fit_curve'])
    # plt.imshow(visual)
    # plt.show()
    left, right, source_pts, dest_pts = resize([result['pixel_left_best_fit_curve'], result['pixel_right_best_fit_curve']],
        SOURCE_PTS, DEST_PTS, SCALE_FACTOR)

    old_certificate =  {'img': low_res, 'left': left, 'right': right,
        'thresholds': REG_THRESHOLDS, 'source': source_pts, 'dest': dest_pts,
        'timestamp': time_stamp, 'signature': signature}
    return old_certificate

class ControllerHandler(socketserver.StreamRequestHandler):
    def handle(self):
        data = []
        while True:
            packet = self.rfile.readline()
            if not packet:
                break
            data.append(packet)
        if data:
            data_arr = pickle.loads(b"".join(data))
            certificate = get_certificate(*data_arr)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, MONITOR_PORT))
                    s.sendall(pickle.dumps(certificate))
            except:
                print('waiting for monitor to establish connection...')

def main():
    print('controller: ', socket.gethostbyname(socket.gethostname()))
    server = socketserver.TCPServer(('', SENSOR_PORT), ControllerHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
