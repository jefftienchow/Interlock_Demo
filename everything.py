import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "sensor"))
sys.path.append(os.path.join(os.path.dirname(__file__), "controller"))
sys.path.append(os.path.join(os.path.dirname(__file__), "monitor"))

from sensor.generate import get_images
from controller.pipeline import get_certificate
from monitor.interlock import run_tests

img, low_res = get_images()
certificate = get_certificate(img, low_res)
print(run_tests(certificate))