import numpy as np
import matplotlib.pyplot as plt
from hashlib import sha512
import pickle
import socketserver
import socket

from birdseye import BirdsEye
from helpers import roi
from lanefilter import LaneFilter
from conformance import conformance_test
from geometric import geometric_test

PORT = 54321

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

    time_stamp = certificate['timestamp']
    signature = certificate['signature']
    pub_key = certificate['pubkey']

    # verify img from controller is correct
    pre_verify = sha512(str(img).encode()+time_stamp.encode()).digest()
    verify_hash = int.from_bytes(pre_verify, byteorder='big')
    signature_hash = pow(signature, pub_key[0], pub_key[1])

    if verify_hash != signature_hash:
        print('Image was tampered with')
        return
    print('Image is legit')

    # TODO: verify reasonable timestamp

    wb = get_binary(img, birds_eye, certificate['thresholds'])
    shape_result = geometric_test(left_line, right_line, img.shape[0])
    left_result = conformance_test(True, left_line, wb)
    right_result = conformance_test(False, right_line, wb)
    result = birds_eye.project(img, wb, left_line, right_line)
    return shape_result, left_result, right_result


class MonitorHandler(socketserver.StreamRequestHandler):
    def handle(self):
        data = []
        while True:
            packet = self.rfile.readline()
            if not packet:
                break
            data.append(packet)
        if data:
            certificate = pickle.loads(b"".join(data))
            result = run_tests(certificate)
            print(result)

def main():
    server = socketserver.TCPServer(('', PORT), MonitorHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
