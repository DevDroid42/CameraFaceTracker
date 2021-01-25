import io
import numpy
from picamera.array import PiRGBArray # Generates a 3D RGB array
from picamera import PiCamera # Provides a Python interface for the RPi Camera Module
import time # Provides time-related functions
from io import BytesIO
import cv2 # OpenCV library
import threading
from flask import Flask, render_template, render_template_string, Response

app = Flask(__name__)

# Initialize the camera
camera = PiCamera()

xres = 160
yres = 120 
# Set the camera resolution
camera.resolution = (xres, yres)
 
# Set the number of frames per second
camera.framerate = 32
 
# Generates a 3D RGB array and stores it in rawCapture
raw_capture = PiRGBArray(camera, size=(xres, yres))
 
face_cascade = cv2.CascadeClassifier('/home/pi/Face/haarcascade_frontalface_default.xml')
# Wait a certain number of seconds to allow the camera time to warmup
time.sleep(0.1)

framelock = threading.Lock()
settinglock = threading.Lock()
poslock = threading.Lock()
pinlock = threading.Lock()

#coords must be editied inside the poslock
coords = [0,0,0,0]

pinStates = [False,False,False,False,False]

#global settings. manipulation music be locked via setting lock
detectFaces = [True]

def record():
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True): 
        # Grab the raw NumPy array representing the image
        image = frame.array        
        #∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨
        settinglock.acquire()        
        if(detectFaces[0]):
            #Convert to grayscale
            gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            #Draw red border to indicate targeting mode is on
            cv2.rectangle(image,(0,0),(xres-1, yres-1),(0,0,255),1)

            #Look for faces in the image using the loaded cascade file
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)
            
            #∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨∨
            poslock.acquire()
            #Draw a rectangle around every found face
            for (x,y,w,h) in faces:
                cv2.rectangle(image,(x,y),(x+w,y+h),(255,255,0),1)
                coords[0] = x
                coords[1] = y
                coords[2] = w
                coords[3] = h
                print ("Found {}" + str(len(faces)) + " face(s)")
                print ("Position X:" + str(x) + " Y:" + str(y) + " W:" + str(w) + " h:" + str(h))
            track(coords)
            poslock.release()
        else:
            #draw green rectangle to indicate targeting is off
            cv2.rectangle(image,(0,0),(xres-1, yres-1),(0,255,0),1)
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        settinglock.release()
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        framelock.acquire()
        cv2.imwrite("stream.jpg",image)
        framelock.release()
        raw_capture.truncate(0)


recThread = threading.Thread(target=record)
recThread.start()


def gen():
    while(True):        
        framelock.acquire()
        jpg = open('stream.jpg', 'rb').read()
        framelock.release()
        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n\r\n')                

#loads main.html
@app.route('/')
def index():
    """Video streaming"""
    return render_template('main.html')

#main.html references this meathod. app.route lets you create "urls" that html can reference
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    #runs the gen meathod to get html code to send to the browser. This includes the generated image on disk
    return Response(gen(),
                mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/button')
def button():
    print("Hello World")
    return render_template('main.html')

@app.route('/disableTracking')
def disableTracking():
    settinglock.acquire()
    detectFaces[0] = False
    settinglock.release()
    return render_template('main.html')

@app.route('/enableTracking')
def enableTracking():
    print("Hello World")
    settinglock.acquire()
    detectFaces[0] = True    
    settinglock.release()
    print(str(detectFaces))
    return render_template('main.html')

@app.route('/facePos')
def getFacePos():
    pinlock.acquire()
    position = ""
    for (coord) in coords:
        position = position + str(coord) + ","
    pinlock.release()
    setPins(pinStates)
    return position

def up():
    pinlock.acquire()
    for index in range(5):
        pinStates[index] = False
    pinStates[2] = True
    pinlock.release()
    setPins(pinStates)
    return None

def down():
    pinlock.acquire()
    for index in range(5):
        pinStates[index] = False
    pinStates[3] = True
    pinlock.release()
    setPins(pinStates)
    return None

def left():
    pinlock.acquire()
    for index in range(5):
        pinStates[index] = False
    pinStates[0] = True
    pinlock.release()
    setPins(pinStates)
    return None

def right():
    pinlock.acquire()
    for index in range(5):
        pinStates[index] = False
    pinStates[1] = True
    pinlock.release()
    setPins(pinStates)
    return None

def fire():
    pinlock.acquire()
    for index in range(5):
        pinStates[index] = False
    pinStates[4] = True
    setPins(pinStates)
    pinlock.release()
    return None

def track(coords):
    xper = coords[0]
    yper = coords[1]
    #print("xPer" + str(xper))
    #print("yPer" + str(yper))
    if(xper > 60):
        right()
    else:
        if(xper < 40):
            left()
        else:
            if(yper < 40):
                down()
            else:
                if(yper > 60):
                    up()
                else:
                    fire()
    return None

#0 is left, 1 is right, 2 is up, 3 is down, 4 is stop
def setPins(pins):
    print(pins)
    #disable all pins
    #wait .3 secs
    #enable selected pin
    return None

if __name__ == '__main__':
    app.run(host="0.0.0.0")