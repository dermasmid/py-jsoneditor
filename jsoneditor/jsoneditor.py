from io import TextIOWrapper
import json
import threading
import webbrowser
import random
import os
import sys
import requests
import mimetypes
import argparse
import csv
import ast
import sys
import pyperclip
from typing import Union
from collections.abc import Mapping
from urllib.parse import urlparse
from wsgiref.simple_server import make_server, WSGIRequestHandler


# Get installation dir
install_dir = os.path.dirname(os.path.realpath(__file__))


class AltWsgiHandler(WSGIRequestHandler):
    def log_message(self, format, *args) -> None:
        if not self.path == '/files/img/favicon.ico':
            # cached per port.
            self.server.number_of_requests += 1
        if self.path == '/close' or (not self.server.keep_running and self.server.number_of_requests == 6):
            self.server._BaseServer__shutdown_request = True


class Server:

    def __init__(
        self,
        data: Union[dict, str],
        callback: callable = None,
        options: dict = None,
        keep_running: bool = False,
        run_in_thread: bool = False,
        is_csv: bool = False,
        title: str = None,
        port: int = None
        ) -> None:
        self.callback = callback
        self.options = options
        self.keep_running = keep_running
        self.run_in_thread = run_in_thread
        self.is_csv = is_csv
        self.title = title
        self.get_random_port(port)
        self.data = self.get_json(data)


    def get_random_port(self, port: int = None):
        self.port = port or random.randint(1023, 65353)


    def send_response(self, status, content_type, respond):
        headers = [('Content-type', content_type)]
        respond(status, headers)


    def get_json(self, source: Union[dict, str, list]) -> dict:
        # Get json data
        retrieved_data = None
        if type(source) is str:
            if self.is_url(source):
                if source.endswith('.csv'):
                    self.is_csv = True
                self.title = self.title or source.split("/")[-1].split("?")[0]
                retrieved_data = requests.get(source).text
            elif self.is_file(source):
                if source.endswith('.csv'):
                    self.is_csv = True
                self.title = self.title or os.path.basename(source)
                retrieved_data = open(source, 'r')
            else:
                retrieved_data = source
            try:
                data = self.load_json(retrieved_data)
            except Exception as e:
                # We were unable to understand the data, so we print
                # it so the user can understand what happened
                print("Input:\n" + source)
                raise e
        
        elif isinstance(source, Mapping):
            # Convert to dict as some mappings are not json serializable
            data = dict(source)
        else:
            # Source is a list
            data = source
        return data


    @staticmethod
    def is_url(source: str) -> bool:
        try:
            result = urlparse(source)
            is_url = all([result.scheme, result.netloc])
        except:
            is_url = False
        return is_url


    @staticmethod
    def is_file(source: str) -> bool:
        return os.path.exists(source)


    def load_json(self, source):
        if self.is_csv:
            if isinstance(source, str):
                # Throws an error if the input is not valid csv
                csv.Sniffer().sniff(source[:1024], delimiters=',:;\t')
                result = list(csv.DictReader(source.split('\n')))
            elif isinstance(source, TextIOWrapper):
                result = list(csv.DictReader(source))
        else:
            if isinstance(source, str):
                try:
                    result = json.loads(source)
                except ValueError:
                    result = ast.literal_eval(source)
            elif isinstance(source, TextIOWrapper):
                result = json.load(source)
        if isinstance(source, TextIOWrapper):
            source.close()
        return result


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
                    'options': self.options,
                    'title': self.title or 'jsoneditor'
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
        server.keep_running = self.keep_running

        if not self.run_in_thread:
            open_browser(self.port)

        server.serve_forever()


# Entry point
def editjson(
    data: Union[dict, str],
    callback: callable = None,
    options: dict = None,
    keep_running: bool = False,
    run_in_thread: bool = False,
    is_csv: bool = False,
    title: str = None,
    port: int = None
    ) -> None:
    keep_running = keep_running or bool(callback)
    server = Server(data, callback, options, keep_running, run_in_thread, is_csv, title, port)

    if server.run_in_thread:
        thread = threading.Thread(target=server.start)
        thread.start()
        open_browser(server.port)
    else:
        server.start()


def open_browser(port: int) -> None:
    browser_opened = webbrowser.open(f'http://localhost:{port}/')
    if not browser_opened:
        print(f"Couldn't launch browser, Please open this link to see the JSON: http://localhost:{port}/")


# cli function
def main() -> None:
    parser = argparse.ArgumentParser(description=('View and edit your JSON data in the browser.'))
    parser.add_argument('data', help='The JSON data, can be valid JSON or a url that will return JSON or a file path.', nargs='?')
    parser.add_argument('-o', help='Add a button that will output the json back to the console.', action='store_true')
    parser.add_argument('-b', help='Keep running in backround.', action='store_true')
    parser.add_argument('-c', help='Get JSON input from clipboard.', action='store_true')
    parser.add_argument('-k', help='Keep alive.', action='store_true')
    parser.add_argument('-e', help='Edit mode.', action='store_true')
    parser.add_argument('-p', help='Server port.')
    parser.add_argument('--out', help='File to output when in edit mode.')
    parser.add_argument('-t', help='Title to display in browser window.')
    parser.add_argument('--csv', help='Input is CSV.', action='store_true')
    args = parser.parse_args()

    options = {}
    if args.o:
        options['callback'] = lambda data: print(json.dumps(data))

    if args.b:
        options['run_in_background'] = True

    if args.k:
        options['keep_running'] = True

    if args.p:
        options['port'] = int(args.p)

    if args.t:
        options['title'] = args.t

    if args.csv:
        options['is_csv'] = True

    if not os.isatty(0):
        options['data'] = ''.join(x for x in sys.stdin)
    else:
        if args.data:
            options['data'] = args.data
        elif args.c:
            options['data'] = pyperclip.paste()
        else:
            raise ValueError('No data passed')

    if args.e:
        def edit_file(json_data: dict):
            file_path = None
            if args.out:
                file_path = args.out
            elif os.path.exists(options['data']):
                file_path = options['data']
            if file_path:
                with open(file_path, 'w') as f:
                    if args.csv or options['data'].endswith('.csv'):
                        csv_fields = json_data[0].keys() if json_data else []
                        writer = csv.DictWriter(f, csv_fields)
                        writer.writeheader()
                        writer.writerows(json_data)
                    else:
                        json.dump(json_data, f)
            else:
                raise ValueError("You have not specified a --out path, I don't know where to save.")
        options['callback'] = edit_file

    editjson(**options)
