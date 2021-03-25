from typing import Union
from flask import Flask
from flask import render_template
import json
from multiprocessing import Process
import time
import webbrowser
import random

# disable flask logs
import logging
import os
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
os.environ['WERKZEUG_RUN_MAIN'] = 'true'


def editjson(data: Union[dict, str]):
    if type(data) is str:
        data = json.loads(data)

    app = Flask('jsoneditor')
    port = random.randint(1023, 65353)

    @app.route('/')
    def jsoneditor():
        return render_template('index.html', data=data)
    
    server = Process(target=app.run, args=('localhost', port))
    server.start()
    webbrowser.open(f'http://localhost:{port}/')
