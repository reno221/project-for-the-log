import os
import time
import sys
import logging
try:
    from pygtail import Pygtail
except:
    os.system('pip3 install pygtail')
    from pygtail import Pygtail

from flask import Flask, render_template, Response, request #flask imports
from robotLibrary import Robot #import custom made robotLib class for abstraction
from camera import CameraStream #imports "camerastream" class from 'camera.py' file located in the same dir as this app.py file
import cv2 #opencv import


direction = 'None'

app = Flask(__name__) #initialize flask object instance
robot = Robot() #initialize robot class instance
cap = CameraStream().start() #initialize camerastream object instance from other file

app.config["SECRET_KEY"] = "SECRETKEYSECRETKEYSECRETKEYSECRETKEYSECRETKEY"
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", True)
app.config["JSON_AS_ASCII"] = False


LOG_FILE = 'app.log'
log = logging.getLogger('__name__')
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
#flask run --host=0.0.0.0



#below is robot-control related endpoints and functions


@app.route('/')
def entry_point():
    log.info("route =>'/env' - hit!")
    return render_template('base.html')

@app.route("/forward", methods = ['GET','POST'])
def forward():
    speedL = int(request.args.get('speedL', default = 50))
    speedR = int(request.args.get('speedR', default = 64))
    timeMS = int(request.args.get('timeMS', default = 1000))
    robot.motorForward(speedL, speedR, timeMS)
    direction = 'Forward......'
    return "<p>forward</p>"


@app.route("/backward", methods = ['GET','POST'])
def backward():
    speedL = int(request.args.get('speedL', default = 50))
    speedR = int(request.args.get('speedR', default = 66))
    timeMS = int(request.args.get('timeMS', default = 1000))
    robot.motorBackward(speedL, speedR, timeMS)
    direction = 'Backward......'
    return "<p>backward</p>"

@app.route("/left", methods = ['GET','POST'])
def left():
    speedL = int(request.args.get('speedL', default = 50))
    speedR = int(request.args.get('speedR', default = 60))
    timeMS = int(request.args.get('timeMS', default = 850)) 
    robot.motorLeft(speedL, speedR, timeMS)
    direction = 'Left......'
    return "<p>left</p>"

@app.route("/right", methods = ['GET','POST'])
def right():
    speedL = int(request.args.get('speedL', default = 50))
    speedR = int(request.args.get('speedR', default = 60))
    timeMS = int(request.args.get('timeMS', default = 850))
    robot.motorRight(speedL, speedR, timeMS)
    direction = 'Right......'
    return "<p>right</p>"


@app.route('/progress')
def progress():
    def generate():
        x = 0
        while x <= 100:
            yield "data:" + str(x) + "\n\n"
            x = x + 10
            time.sleep(0.5)
    return Response(generate(), mimetype='text/event-stream')


@app.route('/log')
def progress_log():

    def generate():
        # for line in Pygtail(LOG_FILE, every_n=1):
        while True:
            yield "data:" + direction + "\n\n"
            # yield direction
            time.sleep(0.5)
    return Response(generate(), mimetype='text/event-stream')


@app.route('/env')
def show_env():
    log.info("route =>'/env' - hit")
    env = {}
    for k, v in request.environ.items():
        env[k] = str(v)
    log.info("route =>'/env' [env]:\n%s" % env)
    return env



#below is camera related endpoints and functions

@app.route('/') #main page route
def index(): #main page function
    return render_template('index.html')

def gen_frame(): #generator function, meaning it runs like over and over again and the yield statement at the end instead of being a return it returns a ton over and over looped
    while cap: #maybe equivalent to while true? i mean its just the class instance so idk
        frame = cap.read() #calls class read method
        convert = cv2.imencode('.jpg', frame)[1].tobytes() #sets 'encode' var to a .jpg encoded frame in some fancy byte thing idk its basically encoding the image and yea
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + convert + b'\r\n') # concate frame one by one and show result, idk whats going on here but it seems to just be like sending a frame with a ton of random stuff that i might need to understand later idk

@app.route('/video_feed') #endpoint where raw video feed is streamed
def video_feed():
    return Response(gen_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame') #returns the running of the gen_frame function alongside some html stuff i guess? idk




if __name__ == '__main__': #some sort of thing that makes it so it always runs threaded and on the network but i dont think it works whatever i still run flask run --host=0.0.0.0
    app.run(host='0.0.0.0', threaded=True)
