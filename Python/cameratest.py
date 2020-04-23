from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2 as cv

camera = PiCamera()
camera.resolution = (800, 450)

rawCapture = PiRGBArray(camera, size=(800, 450))

for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    image = frame.array
    cv.imshow('frame', image)

    rawCapture.truncate(0)

    key = cv.waitKey(1) & 0xFF
    if key == ord('q'):
        break