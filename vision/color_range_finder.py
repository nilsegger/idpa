import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

resolution = (1024, 768)
camera = PiCamera()
camera.resolution = resolution
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=resolution)

time.sleep(1)

# img = cv2.imread("cap/test.PNG")

cv2.namedWindow("mask")
cv2.namedWindow("hsv")
cv2.namedWindow("img")

lb = 0
lr = 0
lg = 0
ub = 255
ur = 255
ug = 255


def on_lb(val):
    global lb
    lb = val


def on_lg(val):
    global lg
    lg = val


def on_lr(val):
    global lr
    lr = val


def on_ub(val):
    global ub
    ub = val


def on_ug(val):
    global ug
    ug = val


def on_ur(val):
    global ur
    ur = val


cv2.createTrackbar("lb", "mask", lb, 255, on_lb)
cv2.createTrackbar("lg", "mask", lg, 255, on_lg)
cv2.createTrackbar("lr", "mask", lr, 255, on_lr)

cv2.createTrackbar("ub", "mask", ub, 255, on_ub)
cv2.createTrackbar("ug", "mask", ug, 255, on_ug)
cv2.createTrackbar("ur", "mask", ur, 255, on_ur)

min_dist = 20
param1 = 50
param2 = 14
max_radius = 0


def on_min_dist(val):
    global min_dist
    min_dist = min_dist


def on_param1(val):
    global param1
    param1 = val
    if param1 < 1:
        param1 = 1


def on_param2(val):
    global param2
    param2 = val
    if param2 < 1:
        param2 = 1


def on_max_radius(val):
    global max_radius
    max_radius = val


cv2.createTrackbar("min_dist", "img", min_dist, 100, on_min_dist)
cv2.createTrackbar("param1", "img", param1, 500, on_param1)
cv2.createTrackbar("param2", "img", param2, 500, on_param2)
cv2.createTrackbar("maxRadius", "img", max_radius, 500, on_max_radius)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    windows = ["img", "hsv", "mask"]

    for window in windows:
        if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
            break

    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    img = frame.array

    img = cv2.flip(img, 0)
    img = cv2.flip(img, 1)
    # show the frame

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_range = np.array([lb, lg, lr])
    upper_range = np.array([ub, ug, ur])
    mask = cv2.inRange(hsv, lower_range, upper_range)

    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, min_dist, param1=param1, param2=param2, minRadius=0,
                               maxRadius=max_radius)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            cv2.circle(img, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)

    cv2.imshow("hsv", hsv)
    cv2.imshow("mask", mask)
    cv2.imshow("img", img)
    key = cv2.waitKey(1)

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

cv2.destroyAllWindows()
cv2.waitKey(1)

print("Summary")
print("Lower range:", [lb, lg, lr])
print("Upper range:", [ub, ug, ur])
print("min_dist:", min_dist)
print("param1:", param1)
print("param2;", param2)
print("maxRadius;", max_radius)
