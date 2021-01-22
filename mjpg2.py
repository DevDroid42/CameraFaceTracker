import io
import numpy
from picamera.array import PiRGBArray # Generates a 3D RGB array
from picamera import PiCamera # Provides a Python interface for the RPi Camera Module
import time # Provides time-related functions
import cv2 # OpenCV library
from flask import Flask, render_template, render_template_string, Response

app = Flask(__name__)

# Initialize the camera
camera = PiCamera()
 
# Set the camera resolution
camera.resolution = (160, 120)
 
# Set the number of frames per second
camera.framerate = 32
 
# Generates a 3D RGB array and stores it in rawCapture
raw_capture = PiRGBArray(camera, size=(160, 120))
 
face_cascade = cv2.CascadeClassifier('/home/pi/Face/haarcascade_frontalface_default.xml')
# Wait a certain number of seconds to allow the camera time to warmup
time.sleep(0.1)
print("==========PRINT WORKS=============")

def gen():
    print("==========GEN WORKS=============")
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

        cv2.imwrite("stream.jpg",image)
        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + open('stream.jpg', 'rb').read() + b'\r\n\r\n')
        raw_capture.truncate(0)


@app.route('/')
def index():
    """Video streaming"""
    #return render_template('index.html')
    return render_template_string('''<html>
<head>
    <title>Video Streaming </title>
</head>
<body>
    <div>
        <h1>Image</h1>
        <img id="img" src="{{ url_for('video_feed') }}" width = "640" height = "640">
    </div>
    <div>
        <h1>Canvas</h1>
        <canvas id="canvas" width="640px" height="480px"></canvas>
    </div>

<script >
    var ctx = document.getElementById("canvas").getContext('2d');
    var img = new Image();
    img.src = "{{ url_for('video_feed') }}";

    // need only for static image
    //img.onload = function(){   
    //    ctx.drawImage(img, 0, 0);
    //};

    // need only for animated image
    function refreshCanvas(){
        ctx.drawImage(img, 0, 0);
    };
    window.setInterval("refreshCanvas()", 50);

</script>

</body>
</html>''')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host="0.0.0.0")