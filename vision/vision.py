from .camera import Camera
import cv2
import numpy as np
import threading


class Vision:

    def __init__(self, camera: Camera):
        self.camera = camera
        self.thread = None
        self.quit_loop = False

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def quit(self):
        self.quit_loop = True

    def run(self):
        while not self.quit_loop:
            frame = self.camera.get_frame()
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                """
                    Bei diesem Code gebrauchte ich https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_Image_Hough%20Circle_Transform.php als Tutorial.
                """
                img = cv2.medianBlur(frame, 5)

                frame_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                lower_range = np.array([10, 255, 255])
                upper_range = np.array([180, 255, 255])
                mask = cv2.inRange(frame_hsv, lower_range, upper_range)

                cv2.imshow("Red detection", mask)

                circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=14, minRadius=0,
                                           maxRadius=0)

                if circles is not None:
                    """
                        Der untenstehende Code bis zu der Variable "mask" ist von https://www.tutorialspoint.com/detection-of-a-specific-color-blue-here-using-opencv-with-python abgeschaut.
                        Er dient dazu alle roten Farben zu erkennen.
                    """

                    # cv2.imshow('Red detection', mask)

                    """
                        Hier ist die fortführung des oberen Codes. https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_Image_Hough%20Circle_Transform.php
                    """
                    circles = np.uint16(np.around(circles))
                    for i in circles[0, :]:
                        circle_color = mask[i[1]][i[0]]  # y, x

                        # Wenn die Farbe 255 (Weiss) ist, wurde es als rot erkannt und ist somit einer unserer Orientierungs Punkte.
                        if circle_color > 200 and circle_color != 255:
                            print(circle_color)
                        if circle_color == 255:
                            cv2.circle(frame_rgb, (i[0], i[1]), i[2], (0, 255, 0), 2)

                cv2.imshow('image', frame_rgb)  # np.hstack([frame, img, cimg]))
            cv2.waitKey(16)
