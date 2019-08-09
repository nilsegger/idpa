import numpy as np
import cv2


img = cv2.imread('vision/test_bild.jpg')
edges = cv2.Canny(img,100,200)
cv2.imshow('image', edges)
cv2.waitKey(0)
cv2.destroyAllWindows()