import matplotlib.pyplot as plt
import numpy as np

from scipy import signal

def conformance_test(left, fit, img):
    h = img.shape[0]
    ypts = np.arange(0, h - 1)

    # filter values are heavier towards the bottom of the filter
    filter_values = np.arange(100, 255, 155/(h-1))
    filter_p = np.poly1d(fit)
    xpts = filter_p(ypts)
    min_x = np.amin(xpts)
    w = int(np.amax(xpts) - np.amin(xpts))

    padding = 10
    fill_val = -2
    filter = np.full((h + padding, w + padding), fill_val).astype(np.uint8)

    for i in range(len(filter_values)):
        # subtracts min_x to account for offset given by fit
        filter[(ypts[i] + padding/2).astype(int), (xpts[i] - min_x + padding/2).astype(int)] = filter_values[i]

    blur = np.full([4, 4], 1 / 16)
    filter = signal.convolve2d(filter, blur)

    half_width = int(img.shape[1]/2)
    if left:
        img = img[:, :half_width]
    else:
        img = img[:, half_width + 1:]

    grad = signal.correlate2d(img, filter, 'same')
    result = np.unravel_index(grad.argmax(), grad.shape)

    p = np.poly1d(fit)
    offset = int(filter.shape[1] / 2) - (xpts[result[0]] - min_x + padding / 2)

    if left:
        actual_x = (result[1] - offset) 
        expected_x = p(result[0] )
    else:
        actual_x = (result[1] + half_width - offset)
        expected_x = p(result[0] )

    if abs(actual_x - expected_x) < 20 and grad[result[0]][result[1]] > 50000:
        return True
    return False
