import io
import picamera
import numpy
from picamera.array import PiRGBArray # Generates a 3D RGB array
from picamera import PiCamera # Provides a Python interface for the RPi Camera Module
import time # Provides time-related functions
import cv2 # OpenCV library
 
# Initialize the camera
camera = PiCamera()
 
# Set the camera resolution
camera.resolution = (320, 240)
 
# Set the number of frames per second
camera.framerate = 32
 
# Generates a 3D RGB array and stores it in rawCapture
raw_capture = PiRGBArray(camera, size=(320, 240))
 
face_cascade = cv2.CascadeClassifier('/home/pi/Face/haarcascade_frontalface_default.xml')
# Wait a certain number of seconds to allow the camera time to warmup
time.sleep(0.1)
 
frameCount = 0
gui = False
# Capture frames continuously from the camera
for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
     
    # Grab the raw NumPy array representing the image
    image = frame.array

    #Convert to grayscale
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    #Look for faces in the image using the loaded cascade file
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    #Draw a rectangle around every found face
    for (x,y,w,h) in faces:
        cv2.rectangle(image,(x,y),(x+w,y+h),(255,255,0),4)
        print ("Found {}" + str(len(faces)) + " face(s)")
        print ("Position X:" + str(x) + " Y:" + str(y) + " W:" + str(w) + " h:" + str(h))

     
    # Clear the stream in preparation for the next frame
    raw_capture.truncate(0)

    if gui:
        # Display the frame using OpenCV
        cv2.imshow("Frame", image)
     
        # Wait for keyPress for 1 millisecond
        key = cv2.waitKey(1) & 0xFF 
        # If the `q` key was pressed, break from the loop
        if key == ord("q"):
            cv2.imwrite("result.jpg",image)
            break