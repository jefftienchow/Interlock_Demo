import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "sensor"))
sys.path.append(os.path.join(os.path.dirname(__file__), "controller"))
sys.path.append(os.path.join(os.path.dirname(__file__), "monitor"))

from sensor.generate import get_images
from controller.pipeline import get_certificate
from monitor.interlock import run_tests

img, low_res, time_stamp, signature, pub_key = get_images()


certificate = get_certificate(img, low_res, time_stamp, signature, pub_key)

#### Man in the middle test ####
# certificate['timestamp'] = '3'+certificate['timestamp'][1:]

print(run_tests(certificate))