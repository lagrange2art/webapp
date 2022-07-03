""" https://projects.raspberrypi.org/en/projects/python-web-server-with-flask/1
this is run at startup. To change this behavior delete call from /etc/rc.local
"""

from flask import Flask, render_template
from ledstrip.fillstrip import lightup
#from PiCam.ambilight import Ambilight

import threading  # create independent thread for ambilight

 
#amblight = Ambilight()

app = Flask(__name__)


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
    lightup(rgb)
    return render_template('fillstrip.html', name=rgb)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', threaded=True)
