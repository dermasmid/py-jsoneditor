import json
import threading
import webbrowser
import random
import os
import sys
import requests
import mimetypes
import argparse
from typing import Union
from collections.abc import Mapping
from urllib.parse import urlparse
from wsgiref.simple_server import make_server, WSGIRequestHandler


# Get installation dir
install_dir = os.path.dirname(os.path.realpath(__file__))


class AltWsgiHandler(WSGIRequestHandler):
    def log_message(self, format, *args) -> None:
        self.server.number_of_requests += 1
        if self.path == '/close' or (not self.server.run_in_background and self.server.number_of_requests == 7):
            self.server._BaseServer__shutdown_request = True


class Server:

    def __init__(self, data: Union[dict, str], callback: callable = None, options: dict = None, run_in_background: bool = False) -> None:
        self.data = self.get_json(data)
        self.callback = callback
        self.options = options
        self.run_in_background = run_in_background
        self.get_random_port()


    def get_random_port(self):
        self.port = random.randint(1023, 65353)


    def send_response(self, status, content_type, respond):
        headers = [('Content-type', content_type)]
        respond(status, headers)


    def get_json(self, data):
        # Get json data
        if type(data) is str:
            try:
                data = json.loads(data)
            except ValueError:
                try:
                    result = urlparse(data)
                    is_url = all([result.scheme, result.netloc])
                except:
                    is_url = False
                if os.path.exists(data):
                    with open(data, 'r') as f:
                        data = json.load(f)
                elif is_url:
                    text_data = requests.get(data).text
                    try:
                        data = json.loads(text_data)
                    except ValueError:
                        raise ValueError('The url passed did not return valid JSON')
                else:
                    raise ValueError('No valid value passed')
        elif isinstance(data, Mapping):
            # convert to dict as some mappings are not json serializable
            data = dict(data)
        return data


    def wsgi_app(self, environ, respond):
        path = environ['PATH_INFO']
        method = environ['REQUEST_METHOD']
        file_path = install_dir + path
        # index.html
        if method == 'GET':
            if path == '/':
                self.send_response('200 OK', 'text/html', respond)
                yield open(install_dir + '/files/index.html', "rb").read()
            # Data endpiont
            elif path == '/get_data':
                self.send_response('200 OK', 'application/json', respond)
                data = {
                    'data': self.data,
                    'callback': bool(self.callback),
                    'options': self.options
                }
                yield json.dumps(data).encode('utf-8')
            # Close endpoint
            elif path == '/close':
                self.send_response('200 OK', 'text/plain', respond)
                yield b''
            # Serve static files
            elif path.startswith('/files') and os.path.exists(file_path):
                type = mimetypes.guess_type(file_path)[0]
                self.send_response('200 OK', type, respond)
                yield open(file_path, "rb").read()
            # 404
            else:
                self.send_response('404 - Not Found', 'text/plain', respond)
                yield b''
        # callback endpoint
        elif method == 'POST':
            if path == '/callback':
                request_body_size = int(environ['CONTENT_LENGTH'])
                callback_data = json.loads(environ['wsgi.input'].read(request_body_size).decode('utf-8'))['data']
                self.callback(callback_data)
                self.send_response('200 OK', 'text/plain', respond)
                yield b''


    def start(self):
        # We might get an error if the port is in use.
        while True:
            try:
                server = make_server('', self.port, self.wsgi_app, handler_class=AltWsgiHandler)
                break
            except OSError:
                self.get_random_port()

        server.number_of_requests = 0
        server.run_in_background = self.run_in_background

        if not self.run_in_background:
            open_browser(self.port)
        
        server.serve_forever()


# Entry point
def editjson(data: Union[dict, str], callback: callable = None, options: dict = None, run_in_background: bool = False) -> None:
    server = Server(data, callback, options, run_in_background or bool(callback))

    if server.run_in_background:
        thread = threading.Thread(target=server.start)
        thread.start()
        open_browser(server.port)
    else:
        server.start()


def open_browser(port: int) -> None:
    browser_opened = webbrowser.open(f'http://localhost:{port}/')
    if not browser_opened:
        print(f"couldn't launch brower, Please open this link to see the JSON: http://localhost:{port}/")


# cli function
def main() -> None:
    parser = argparse.ArgumentParser(description=('View and edit your JSON data in the browser.'))
    parser.add_argument('data', help='The JSON data, can be valid JSON or a url that will return JSON or a file path.', nargs='?')
    parser.add_argument('-o', help='Add a button that will output the json back to the console.', action='store_true')
    parser.add_argument('-b', help='Keep running in backround.', action='store_true')
    args = parser.parse_args()

    options = {}
    if args.o:
        options['callback'] = print

    if args.b:
        options['run_in_background'] = True

    if not os.isatty(0):
        options['data'] = ''.join(x for x in sys.stdin)
    else:
        if args.data:
            options['data'] = args.data
        else:
            raise ValueError('No data passed')

    editjson(**options)
