import numpy as np
import cv2
import sys

min_value = 100
max_value = 200

def on_min_trackbar(value):
    global min_value
    min_value = int(value)


def on_max_trackbar(value):
    global max_value
    max_value = int(value)


def prepare_image(path, mock=False):
    global min_value
    global max_value

    img = cv2.imread(path)

    if img.shape[1] > 500:
        scale = 500 / img.shape[1]
        img = cv2.resize(img, (500, int(img.shape[0] * scale)))

    edges = None

    step = 50

    if not mock:

        cv2.namedWindow("Image Edges")
        cv2.startWindowThread()
        cv2.createTrackbar("min_value", "Image Edges", min_value, 3000, on_min_trackbar)
        cv2.createTrackbar("max_value", "Image Edges", max_value, 3000, on_max_trackbar)

        confirmed = False
        while not confirmed and cv2.getWindowProperty('Image Edges', cv2.WND_PROP_VISIBLE) > 0:
            edges = cv2.Canny(img, min_value, max_value)

            cv2.imshow('Image Edges', np.hstack([img, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)]))

            key = cv2.waitKey(1)

            if key == 105:  # I
                max_value += step

            elif key == 107:  # K
                max_value -= step

            elif key == 119:  # W
                min_value += step

            elif key == 115:  # S
                min_value -= step

            elif key == 13:  # Enter
                confirmed = True

        cv2.destroyWindow("Image Edges")
        cv2.waitKey(1)

        if not confirmed:
            exit(-1)

    else:
        edges = cv2.Canny(img, min_value, max_value)
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    return edges



def optimize_path(image_to_print, precision = 2):

    height, width, _ = image_to_print.shape
    path = []

    step = precision
    y = height - 1

    vertical_steps = height / step
    horizontal_steps = width / step

    for v_step in range(int(vertical_steps)):

        print(int(100 / vertical_steps * v_step), "%")

        for h_step in range(int(horizontal_steps)):
            y1 = v_step * step
            x1 = h_step * step

            pixels = []

            for y in range(int(step)):

                for x in range(int(step)):

                    if (image_to_print[int((y + y1))][int((x + x1))][0] != 0) or (
                            image_to_print[int((y + y1))][int((x + x1))][1] != 0) or (
                            image_to_print[int((y + y1))][int((x + x1))][2] != 0):
                        pixels.append((int(x + x1), int(y + y1)))

            if len(pixels) == 1:
                path.append(pixels[0])
            elif len(pixels) > 1:
                path.append((int(x1 + step), int(y1 + step)))


    if len(path) == 0:
        print("There were no white pixels.")
        exit(-1)

    overlay_image = np.zeros(image_to_print.shape, np.uint8)

    for p in path:

        if p[1] < height and p[0] < width:
            overlay_image[p[1]][p[0]] = (0, 255, 0)

    cv2.imshow("Resultat", np.hstack([image_to_print, overlay_image]))
    cv2.waitKey(0)

if len(sys.argv) >= 2:
    img = prepare_image(sys.argv[1])
    optimize_path(img)