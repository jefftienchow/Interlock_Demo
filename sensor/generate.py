import random
import cv2
import os

TOP_CROP = 360
X_CROP = 150
SCALE_FACTOR = 1/5

def crop(img, top_crop, x_crop):
    img = img[top_crop:, x_crop:img.shape[1] - x_crop]
    return img

def get_images():
    rand = random.SystemRandom().randrange(9)
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    image = cv2.imread(os.path.join(__location__, 'test_images/test' + str(rand) + '.jpg'))
    cropped = crop(image, TOP_CROP, X_CROP)
    low_res = cv2.resize(cropped, (int(cropped.shape[1] * SCALE_FACTOR), int(cropped.shape[0] * SCALE_FACTOR)))
    return cropped, low_res
