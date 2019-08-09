from sim_objects.tkinter_window import Window
import cv2
import numpy as np


class Camera:

    def get_frame(self):
        pass

    def get_markers(self):
        pass


class SimulationCamera(Camera):

    def __init__(self, window: Window):
        self.window = window

    def get_frame(self):
        return self.window.get_frame()

    def get_markers(self):
        frame = self.get_frame()
        if frame is not None:
            """
                Bei diesem Code gebrauchte ich https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_Image_Hough%20Circle_Transform.php als Tutorial.
            """
            # img = cv2.medianBlur(frame, 5)
            frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            """
            Richtiges Farbgebiet zu finden scheint mir fast unmöglich zu sein.
            
            Farbe welche ich für die Punkte verwende ist in RGB 255, 129, 100. 
            Im BGR System welches OpenCV benutzt ist dies natürlich 100, 129, 255.
            Benutze ich diesen Wert für lower_range und upper_range kann es die Punkte nicht erkennen.
            Für die upper_range ist eine gute Regel den BGR Wert zu nehmen und bei jedem Wert einfach plus etwa 30 bis 50 zu rechnen und danach sollte es damit funktionieren.
            """

            lower_range = np.array([100, 129, 255])
            upper_range = np.array([150, 150, 255])
            mask = cv2.inRange(frame_hsv, lower_range, upper_range)

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

                markers = []
                circles = np.uint16(np.around(circles))
                for i in circles[0, :]:
                    circle_color = mask[i[1]][i[0]]  # y, x

                    # Wenn die Farbe 255 (Weiss) ist, wurde es als rot, beziehungsweise blau wegen der Verwechslung von BGR und RGB, erkannt und ist somit einer unserer Orientierungs Punkte.
                    if circle_color == 255:
                        markers.append((i[0], i[1], i[2]))

                if len(markers) == 0:
                    return None
                else:

                    """
                        Sortierung der Markierungen.
                        0. Linke Befestigung an der Wand
                        1. Rechte Befestgung an der Wand
                        2. Linker Motor
                        3. Rechter Motor
                    """

                    sorted_markers = [markers[0]]

                    for i in range(1, len(markers)):
                        inserted = False
                        x, y, r = markers[i]
                        for q in range(len(sorted_markers)):
                            qx, qy, qr = sorted_markers[q]
                            if y < qy:
                                sorted_markers.insert(0, markers[i])
                                inserted = True
                                break
                        if not inserted:
                            sorted_markers.append(markers[i])

                    if len(sorted_markers) >= 2:
                        x, y, r = sorted_markers[0]
                        sx, sy, sr = sorted_markers[1]
                        if sx < x:
                            sorted_markers[0] = (sx, sy, sr)
                            sorted_markers[1] = (x, y, r)

                    if len(sorted_markers) == 4:
                        x, y, r = sorted_markers[2]
                        sx, sy, sr = sorted_markers[3]
                        if sx < x:
                            sorted_markers[2] = (sx, sy, sr)
                            sorted_markers[3] = (x, y, r)

                    if len(sorted_markers) > 4:
                        print("Zu viele Markierungen.")

                    return markers
            else:
                return None
