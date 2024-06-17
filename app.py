""" https://projects.raspberrypi.org/en/projects/python-web-server-with-flask/1
this is run at startup using systemd. Created file /lib/systemd/system/rpitv.service
essentially with content python /home/pi/Documents/webapp/app.py. 
Then start service with: sudo systemctl start rpitv.service
If it works, then stop service: sudo systemctl stop rpitv.service
Enable service to run on startup: sudo systemctl enable rpitv.service
"""
import numpy as np
import time
from matplotlib.pyplot import get_cmap
from matplotlib import cm
from matplotlib.colors import Normalize

import sys
libpath = '/home/pi/Documents'
if libpath not in sys.path:
    sys.path.append(libpath)

from flask import Flask, render_template, request
import threading 

import board
import neopixel
from ADCDevice import *

from PiMic.ledctrl import AudioVisual
from ledstrip.fillstrip import lightup
from ledstrip.motion import Rotate, Strobo
#from PiCam.ambilight import Ambilight

class FlaskAppWrapper(object):
    def __init__(self, app, **kwargs):
        self.app = app
        self.brightness = kwargs['brightness']
        
        self.pixels = neopixel.NeoPixel(board.D10, 219, brightness=1, auto_write=False)
        self.adc = ADS7830()

        self.rotate = Rotate(self.pixels)
        self.strobo = Strobo(self.pixels)
        self.audiovisual = AudioVisual(self.adc, self.pixels)


    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=['GET'], *args, **kwargs):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods, *args, **kwargs)
    
    def run(self, **kwargs):
        self.app.run(**kwargs)
        

def index():
    """ home screen of website. load content from template folder"""
    app.rotate.STOP_THREAD = True
    app.audiovisual.STOP_THREAD = True     
    app.strobo.STOP_THREAD = True
    return render_template('index.html')


def fillstrip(rgb):
    """ When URL fillstrip/rgb is requested the led strip lights up
    according to rgb values. 
    param str rgb: string with comma seperated rgb values """
    # adjust brightness of rgb = 'r,g,b'
    rgb = np.array(rgb.split(',')).astype(int)   # rgb = [r,g,b]
    rgb = (app.brightness*rgb).astype(int)
    rgb = ','.join(rgb.astype(str))              # rgb = 'r,g,b'
    if type(rgb) == str:
        rgbvals = np.array(rgb.split(',')).astype(int)
    else:
        rgbvals = rgb
    app.pixels.fill((rgbvals[0], rgbvals[1], rgbvals[2]))
    app.pixels.show()

    return render_template('fillstrip.html', name=rgb)


def set_brightness(rgb):
    """ use interface on webapp to change global variable that changes brightness"""
    global brightness
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        # set new brightness
        app.brightness = float(request.form['Brightness'])
        # show new brightness if 'update' button is pressed
        fillstrip(rgb)
        return render_template('fillstrip.html', name=rgb)


def animation():
    length = len(app.pixels)
    cmap = get_cmap('hsv')#'plasma')#viridis')#spring')#twilight')#
    norm = Normalize(vmin=0, vmax=length)
    scalarMap = cm.ScalarMappable(norm=norm, cmap=cmap)
    colors = ((scalarMap.to_rgba(np.arange(length))*255)[:,:3]).astype(int)      

    thread = threading.Thread(target=app.rotate.run, args=(colors, -1))
    app.strobo.STOP_THREAD = True
    app.rotate.STOP_THREAD = False
    thread.start()
    
    return render_template('animation.html')

def strobo():
    thread = threading.Thread(target=app.strobo.run)
    app.rotate.STOP_THREAD = True
    app.strobo.STOP_THREAD = False
    thread.start()
    return render_template('animation.html')

def audiovis(method='ladder'):
    print(type(method))
    thread = threading.Thread(target=app.audiovisual.run, args=(method,))
    app.audiovisual.STOP_THREAD = False
    thread.start()
    return render_template('audiovisual.html', name=method)




flask_app = Flask(__name__)
app = FlaskAppWrapper(flask_app, brightness=0.5)

app.add_endpoint('/', '', index, methods=['GET'])
app.add_endpoint('/fillstrip/<rgb>', 'fillstrip', fillstrip, methods=['GET'])
app.add_endpoint('/fillstrip/<rgb>', 'setbrightness', set_brightness, methods=['POST', 'GET'])
app.add_endpoint('/animation/', 'animation', animation)
app.add_endpoint('/animation/strobo/', 'strobo', strobo)

app.add_endpoint('/audiovisual/<method>', 'audiovisual', audiovis, methods=['GET'])


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', threaded=True)


