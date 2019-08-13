import cv2
import numpy as np


def prepare_image(path, mock=True):
    img = cv2.imread(path)
    edges = None
    min = 650
    max = 1300
    step = 50

    if not mock:
        confirmed = False
        while not confirmed:
            print(min, max)
            edges = cv2.Canny(img, min, max)
            cv2.imshow('image', edges)
            key = cv2.waitKey(0)

            if key == 105:  # I
                max += step

            elif key == 107:  # K
                max -= step

            elif key == 119:  # W
                min += step

            elif key == 115:  # S
                min -= step

            elif key == 13:  # Enter
                confirmed = True
            else:
                print("Key", key, "not recognized.")

        cv2.destroyWindow('image')
    else:
        edges = cv2.Canny(img, min, max)

    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    return edges
