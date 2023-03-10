""" https://projects.raspberrypi.org/en/projects/python-web-server-with-flask/1
this is run at startup. To change this behavior delete call from /etc/rc.local
"""

from flask import Flask, render_template, request
from ledstrip.fillstrip import lightup
from ledstrip.motion import animation

#from PiCam.ambilight import Ambilight

import threading  # create independent thread for ambilight

import numpy as np
 
#amblight = Ambilight()

app = Flask(__name__)

brightness = 0.5   # initial brightness

@app.route('/')
def index():
    """ home screen of website. load content from template folder"""
    return render_template('index.html')

# this function is executed when someone requests the URL ambilight
@app.route('/ambilight')
def ambilight():
    """ Start ambient light when someone request URL /ambilight.
    Use thread so that it is possible to terminate it."""
    #amblight._FINISH = False
    #thread = threading.Thread(target=amblight.run())
    #thread.start()    
    
    return render_template('ambilight.html') 

@app.route('/fillstrip/<rgb>')
def fillstrip(rgb):
    """ When URL fillstrip/rgb is requested the led strip lights up
    according to rgb values. 
    param str rgb: string with comma seperated rgb values """
    #amblight._FINISH = True  # stop ambilight if running        

    # adjust brightness of rgb = 'r,g,b'
    rgb = np.array(rgb.split(',')).astype(int)   # rgb = [r,g,b]
    rgb = (brightness*rgb).astype(int)
    rgb = ','.join(rgb.astype(str))              # rgb = 'r,g,b'
    lightup(rgb)
    return render_template('fillstrip.html', name=rgb)

@app.route('/fillstrip/<rgb>', methods=['POST', 'GET'])
def set_brightness(rgb):
    """ use interface on webapp to change global variable that changes brightness"""
    global brightness
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        # set new brightness
        brightness = float(request.form['Brightness'])
        # show new brightness if 'update' button is pressed
        fillstrip(rgb)
        return render_template('fillstrip.html', name=rgb)


@app.route('/animation/')
def animate():
    animation()

    return render_template('animation.html')
    

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', threaded=True)
