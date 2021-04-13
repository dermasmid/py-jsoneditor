from typing import Union
from flask import Flask, request
from flask import render_template
import json
from multiprocessing import Process
import time
import webbrowser
import random
import os
import sys

# get installation dir
install_dir = os.path.dirname(os.path.realpath(__file__))

# disable flask logs
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
os.environ['WERKZEUG_RUN_MAIN'] = 'true'


def editjson(data: Union[dict, str], finnish_callback: callable = None, options: dict = None):
    if type(data) is str:
        data = json.loads(data)

    app = Flask('jsoneditor', template_folder= install_dir + '/templates')
    port = random.randint(1023, 65353)

    @app.route('/')
    def jsoneditor_route():
        return render_template('index.html', data=data, send_back_json= bool(finnish_callback), options= options)

    if finnish_callback:
        @app.route('/post', methods=['POST'])
        def callback_route():
            data = request.json['data']
            finnish_callback(data)
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    
    server = Process(target=app.run, args=('localhost', port))
    server.start()
    webbrowser.open(f'http://localhost:{port}/')

def main():
    if not os.isatty(0):
        data = ''.join(x for x in sys.stdin)
    else:
        if len(sys.argv) == 2:
            data = sys.argv[1]
        else:
            raise Exception('Got invalid number of arguments')

    editjson(data)
