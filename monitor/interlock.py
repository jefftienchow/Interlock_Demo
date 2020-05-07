import os
import numpy as np
import matplotlib.pyplot as plt
from Crypto.PublicKey import RSA
from hashlib import sha512
import pickle
import socketserver
import socket
import _thread as thread

from birdseye import BirdsEye
from helpers import roi
from lanefilter import LaneFilter
from conformance import conformance_test
from geometric import geometric_test

CONTROLLER_PORT = 54321
ACTUATOR_PORT = 12345
SENSOR_PORT = 23456


class MonitorKey():
    def __init__(self):
        self.key = None
    
monitor_key = MonitorKey()

if os.environ.get('PROD'):
    HOST = '172.168.0.130'
else:
    HOST = '127.0.1.1'

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

def get_public_key():
    fname = os.path.join(os.path.dirname(__file__), 'pubkey.pem')

    f = open(fname,'r')
    key = RSA.importKey(f.read())

    return (key.e, key.n)

def run_tests(certificate):
    img = certificate['img']
    left_line = certificate['left']
    right_line = certificate['right']
    birds_eye = BirdsEye(certificate['source'], certificate['dest'])

    time_stamp = certificate['timestamp']
    signature = certificate['signature']
    pub_key = get_public_key()

    # verify img from controller is correct
    pre_verify = sha512(str(img).encode()+time_stamp.encode()).digest()
    verify_hash = int.from_bytes(pre_verify, byteorder='big')
    signature_hash = pow(signature, pub_key[0], pub_key[1])

    if verify_hash != signature_hash:
        print('Image was tampered with')
        return False
    print('Image is legit')

    # TODO: verify reasonable timestamp

    wb = get_binary(img, birds_eye, certificate['thresholds'])
    shape_result = geometric_test(left_line, right_line, img.shape[0])
    left_result = conformance_test(True, left_line, wb)
    right_result = conformance_test(False, right_line, wb)
    result = birds_eye.project(img, wb, left_line, right_line)
    
    if shape_result and left_result and right_result: 
        return True
    print('failed a test')
    return False


def main():
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
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((HOST, ACTUATOR_PORT))
                        s.sendall(pickle.dumps(result))
                except:
                    print('waiting for actuator to establish connection...')

    class SensorHandler(socketserver.StreamRequestHandler):
        def handle(self):
            key = self.request.recv(1024)
            # store the key here
            monitor_key.key = key
            print("sending ack")
            self.request.send(b"ack")
            def kill_server(server):
                server.shutdown()
            thread.start_new_thread(kill_server, (sensor_server,))

    print('interlock: ', socket.gethostbyname(socket.gethostname()))
    sensor_server = socketserver.TCPServer(('', SENSOR_PORT), SensorHandler)
    sensor_server.serve_forever()
    
    print('monitor key is received; interlock is now functional')

    controller_server = socketserver.TCPServer(('', CONTROLLER_PORT), MonitorHandler)
    controller_server.serve_forever()
    

if __name__ == "__main__":
    main()
