import cv2
import numpy as np


def prepare_image(path, mock=False):
    img = cv2.imread(path)
    edges = None
    min = 100
    max = 200
    step = 50

    if not mock:
        confirmed = False
        while not confirmed:
            print("Bereich min:", min, "max:", max)
            edges = cv2.Canny(img, min, max)
            cv2.imshow('Image Edges', np.hstack([img, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)]))
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
            elif key == -1:  # Fenster schliessen
                cv2.destroyWindow('Image Edges')
                exit(-1)
            else:
                print("Key", key, "not recognized.")

        cv2.destroyWindow('Image Edges')
    else:
        edges = cv2.Canny(img, min, max)

    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    return edges
