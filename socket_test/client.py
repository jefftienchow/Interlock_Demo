import socket
import pickle
import cv2
import sys
import time

TOP_CROP = 360
X_CROP = 150
SCALE_FACTOR = 1/5

def crop(img, top_crop, x_crop):
    img = img[top_crop:, x_crop:img.shape[1] - x_crop]
    return img

def main():
    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 65432        # The port used by the server
    for i in range(7):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            image = cv2.imread('test_images/test' + str(i) + '.jpg')
            cropped = crop(image, TOP_CROP, X_CROP)
            low_res = cv2.resize(cropped, (int(cropped.shape[1] * SCALE_FACTOR), int(cropped.shape[0] * SCALE_FACTOR)))
            s.sendall(pickle.dumps(image))
        time.sleep(5)



if __name__ == '__main__':
    main()