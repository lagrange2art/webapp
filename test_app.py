""" https://projects.raspberrypi.org/en/projects/python-web-server-with-flask/1"""

from flask import Flask, render_template
from picamera import PiCamera


app = Flask(__name__)


@app.route('/')
def index():
    """ home screen of website. load content from template folder"""
    return render_template('index.html')

@app.route('/ambilight')
def ambilight():
    """ create new page under link ambilight"""
    cam = PiCamera() 
    return render_template('ambilight.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
