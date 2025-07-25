# test_camera.py
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.start_preview()
picam2.start()
input("Drücke Enter zum Beenden...")
picam2.stop()
