import random
import cv2
import os
import datetime
import socket
import pickle
import time

from Crypto.PublicKey import RSA
from hashlib import sha512

if os.environ.get('PROD'):
    CONTROLLER_HOST = '172.168.1.5'  # The server's hostname or IP address
    MONITOR_HOST = '172.168.0.5'
else:
    CONTROLLER_HOST = '127.0.1.1'
    MONITOR_HOST = '127.0.1.1'

CONTROLLER_PORT = 65432        # The port used by the server
MONITOR_PORT = 23456

class SensorKey():
    def __init__(self):
        self.privkey = None
        self.pubkey = None

sensor_key = SensorKey()

TOP_CROP = 360
X_CROP = 150
SCALE_FACTOR = 1/5

def crop(img, top_crop, x_crop):
    img = img[top_crop:, x_crop:img.shape[1] - x_crop]
    return img

def get_images():
    rand = random.SystemRandom().randrange(8)
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    image = cv2.imread(os.path.join(__location__, 'test_images/test' + str(rand) + '.jpg'))
    cropped = crop(image, TOP_CROP, X_CROP)
    low_res = cv2.resize(cropped, (int(cropped.shape[1] * SCALE_FACTOR), int(cropped.shape[0] * SCALE_FACTOR)))

    time_stamp, signature = gen_signature(low_res)

    return cropped, low_res, time_stamp, signature

def gen_signature(image):
    # fname = os.path.join(os.path.dirname(__file__), 'privkey.pem')

    # # check if key not stored yet
    # if not os.path.exists(fname) or os.path.getsize(fname) == 0:
    #     gen_and_write_keys()

    # f = open(fname,'r')
    # key = RSA.importKey(f.read())

    # if sensor_key.privkey == None:
    #     gen_and_write_keys()

    key = RSA.importKey(sensor_key.privkey.decode())

    # Example: of the form '2020-05-06 22:47:09.850234 '
    time_stamp = str(datetime.datetime.now())

    pre_signature = sha512(str(image).encode()+time_stamp.encode()).digest()

    hashed = int.from_bytes(pre_signature, byteorder='big')
    signature = pow(hashed, key.d, key.n)
    #pub_key = (key.e, key.n)

    return time_stamp, signature

def gen_and_write_keys():
    key = RSA.generate(bits=1024)

    # fname1 = os.path.join(os.path.dirname(__file__), 'privkey.pem')
    # f1 = open(fname1,'wb')
    # f1.write(key.exportKey('PEM'))
    # f1.close()

    sensor_key.privkey = key.exportKey('PEM')

    # fname2 = os.path.join(os.path.dirname(__file__), 'pubkey.pem')
    # f2 = open(fname2,'wb')
    # f2.write(key.publickey().exportKey('PEM'))
    # f2.close()

    sensor_key.pubkey = key.publickey().exportKey('PEM')

def main():
    print('sensor: ', socket.gethostbyname(socket.gethostname()))

    gen_and_write_keys()

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((MONITOR_HOST, MONITOR_PORT))
                key = sensor_key.pubkey # put real key here
                print("key is ", key)
                s.sendall(key)
                ack = s.recv(16)
                print('ack is: ', ack)
                if ack == b"ack":
                    break
        except:
            print('waiting for monitor to establish connection...')
        time.sleep(2)


    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((CONTROLLER_HOST, CONTROLLER_PORT))
                package = get_images()
                s.sendall(pickle.dumps(package))
        except Exception as e:
            print(e)
            print('waiting for controller to establish connection...')
        time.sleep(2)
            

if __name__ == '__main__':
    # gen_and_write_keys()
    # gen_signature()
    main()
