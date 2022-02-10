import argparse
import ast
import csv
import json
import mimetypes
import os
import random
import subprocess
import sys
import threading
import webbrowser
from collections.abc import Mapping
from io import TextIOWrapper
from typing import Any, Callable, Union
from urllib.parse import urlparse
from wsgiref.simple_server import WSGIRequestHandler, make_server

import pyperclip
import requests

# Get installation dir
INSTALL_DIR = os.path.dirname(os.path.realpath(__file__))
RESOURCES = [
    "/",
    "/files/jsoneditor.min.css",
    "/files/index.css",
    "/files/jsoneditor.min.js",
    "/files/index.js",
    "/get_data",
    "/files/img/jsoneditor-icons.svg",
    "/files/img/favicon.ico",
]


class AltWsgiHandler(WSGIRequestHandler):
    def log_message(self, _format, *args) -> None:
        if self.path in self.server.resources:
            self.server.resources.remove(self.path)
        if self.path == "/close" or (
            not self.server.keep_running and not self.server.resources
        ):
            self.server.stop()


class Server:
    def __init__(
        self,
        data: Union[dict, str, list],
        callback: Callable[[dict], Any] = None,
        options: dict = None,
        additional_js: str = None,
        keep_running: bool = False,
        run_in_thread: bool = False,
        is_csv: bool = False,
        is_ndjson: bool = False,
        is_js_object: bool = False,
        title: str = None,
        port: int = None,
        no_browser: bool = False,
    ) -> None:
        self.callback = callback
        self.options = options
        self.additional_js = additional_js
        self.keep_running = keep_running
        self.run_in_thread = run_in_thread
        self.is_csv = is_csv
        self.is_ndjson = is_ndjson
        self.is_js_object = is_js_object
        self.title = title
        self.no_browser = no_browser
        self.get_random_port(port)
        self.data = self.get_json(data)
        self.server = None

    def get_random_port(self, port: int = None):
        self.port = port or random.randint(1023, 65353)

    def send_response(
        self, status: str, content_type: str, respond: Callable, cache: bool = False
    ):
        headers = [("Content-type", content_type)]
        if cache:
            headers.append(("Cache-Control", "max-age=259200"))
        respond(status, headers)

    def get_json(self, source: Union[dict, str, list]) -> dict:
        # Get json data
        retrieved_data = None
        if type(source) is str:
            if self.is_url(source):
                self.detect_source_by_filename(source)
                self.title = self.title or source.split("/")[-1].split("?")[0]
                retrieved_data = requests.get(source).text
            elif self.is_file(source):
                self.detect_source_by_filename(source)
                self.title = self.title or os.path.basename(source)
                retrieved_data = open(source, "r", encoding="utf-8")
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

    def detect_source_by_filename(self, source: str):
        if source.endswith(".csv"):
            self.is_csv = True
        elif any(source.endswith(ext) for ext in [".ndjson", ".jsonl"]):
            self.is_ndjson = True

    def load_json(self, source):
        if self.is_csv:
            if isinstance(source, str):
                # Throws an error if the input is not valid csv
                csv.Sniffer().sniff(source[:1024], delimiters=",:;\t")
                result = list(csv.DictReader(source.split("\n")))
            elif isinstance(source, TextIOWrapper):
                result = list(csv.DictReader(source))
        elif self.is_ndjson:
            if isinstance(source, str):
                lines = source.splitlines()
            elif isinstance(source, TextIOWrapper):
                lines = source.readlines()
            result = list(json.loads(line) for line in lines)
        elif self.is_js_object:
            try:
                result = json.loads(
                    subprocess.run(
                        ["node", "-e", f"console.log(JSON.stringify({source}))"],
                        capture_output=True,
                        check=True,
                    ).stdout.decode()
                )
            except FileNotFoundError:
                print(
                    "You need to have Nodejs installed to be able to use JavaScript Objects."
                )
                sys.exit(1)
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
        path = environ["PATH_INFO"]
        method = environ["REQUEST_METHOD"]
        file_path = INSTALL_DIR + path
        # index.html
        if method == "GET":
            if path == "/":
                self.send_response("200 OK", "text/html", respond)
                with open(INSTALL_DIR + "/files/index.html", "rb") as f:
                    content = f.read()
                yield content
            # Data endpiont
            elif path == "/get_data":
                self.send_response("200 OK", "application/json", respond)
                data = {
                    "data": self.data,
                    "callback": bool(self.callback),
                    "options": self.options,
                    "additional_js": self.additional_js,
                    "title": self.title or "jsoneditor",
                    "keep_running": self.keep_running,
                }
                yield json.dumps(data, default=repr).encode("utf-8")
            # Close endpoint
            elif path == "/close":
                self.send_response("200 OK", "text/plain", respond)
                yield b""
            # Serve static files
            elif path.startswith("/files") and os.path.exists(file_path):
                mimetype = mimetypes.guess_type(file_path)[0]
                self.send_response("200 OK", mimetype, respond, True)
                with open(file_path, "rb") as f:
                    content = f.read()
                yield content
            # 404
            else:
                self.send_response("404 Not Found", "text/plain", respond)
                yield b""
        # callback endpoint
        elif method == "POST":
            if path == "/callback":
                request_body_size = int(environ["CONTENT_LENGTH"])
                callback_data = json.loads(
                    environ["wsgi.input"].read(request_body_size).decode("utf-8")
                )["data"]
                self.callback(callback_data)
                self.send_response("200 OK", "text/plain", respond)
                yield b""

    def start(self):
        # We might get an error if the port is in use.
        while True:
            try:
                self.server = make_server(
                    "", self.port, self.wsgi_app, handler_class=AltWsgiHandler
                )
                break
            except OSError:
                self.get_random_port()

        self.server.resources = RESOURCES.copy()

        self.server.keep_running = self.keep_running
        self.server.stop = self.stop

        if not self.run_in_thread:
            open_browser(self.port, self.no_browser)

        self.server.serve_forever()

    def stop(self):
        if self.server:
            self.server._BaseServer__shutdown_request = True
            self.server.server_close()


# Entry point
def editjson(
    data: Union[dict, str, list],
    callback: Callable[[dict], Any] = None,
    options: dict = None,
    additional_js: str = None,
    keep_running: bool = False,
    run_in_thread: bool = False,
    is_csv: bool = False,
    is_ndjson: bool = False,
    is_js_object: bool = False,
    title: str = None,
    port: int = None,
    no_browser: bool = False,
) -> Server:
    keep_running = keep_running or bool(callback)

    server = Server(
        data,
        callback,
        options,
        additional_js,
        keep_running,
        run_in_thread,
        is_csv,
        is_ndjson,
        is_js_object,
        title,
        port,
        no_browser,
    )

    if server.run_in_thread:
        thread = threading.Thread(target=server.start)
        thread.start()
        open_browser(server.port, no_browser)
    else:
        server.start()

    return server


def open_browser(port: int, no_browser: bool) -> None:
    if no_browser:
        print(f"Please open this link to see the JSON: http://localhost:{port}/")
    else:
        browser_opened = webbrowser.open(f"http://localhost:{port}/")
        if not browser_opened:
            print(
                f"Couldn't launch browser, Please open this link to see the JSON: http://localhost:{port}/"
            )


# cli function
def main() -> None:
    from . import __version__

    parser = argparse.ArgumentParser(
        description=("View and edit your JSON data in the browser.")
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )
    parser.add_argument(
        "data",
        help="The data, can be the raw data or a url that will return the data or a file path",
        nargs="?",
    )
    parser.add_argument(
        "-o",
        help="Add a button that will output the JSON back to the console",
        action="store_true",
    )
    parser.add_argument("-b", help="Keep running in background", action="store_true")
    parser.add_argument("-c", help="Get data input from clipboard", action="store_true")
    parser.add_argument("-k", help="Keep alive", action="store_true")
    parser.add_argument("-e", help="Edit mode", action="store_true")
    parser.add_argument("-n", help="Don't launch browser", action="store_true")
    parser.add_argument("-p", help="Server port")
    parser.add_argument("--out", help="File to output when in edit mode")
    parser.add_argument("-t", help="Title to display in browser window")
    parser.add_argument("--csv", help="Input is CSV", action="store_true")
    parser.add_argument(
        "--js", help="Input is a JavaScript Object", action="store_true"
    )
    parser.add_argument(
        "--ndjson", help="Input is Newline Delimited JSON", action="store_true"
    )
    args = parser.parse_args()

    options = {}
    if args.o:
        options["callback"] = lambda data: print(json.dumps(data))

    if args.b:
        options["run_in_background"] = True

    if args.k:
        options["keep_running"] = True

    if args.p:
        options["port"] = int(args.p)

    if args.t:
        options["title"] = args.t

    if args.n:
        options["no_browser"] = True

    if args.csv:
        options["is_csv"] = True

    if args.js:
        options["is_js_object"] = True

    if args.ndjson:
        options["is_ndjson"] = True

    if not os.isatty(0):
        options["data"] = "".join(x for x in sys.stdin)
    else:
        if args.data:
            options["data"] = args.data
        elif args.c:
            options["data"] = pyperclip.paste()
        else:
            raise ValueError("No data passed")

    if args.e:

        def edit_file(json_data: dict):
            file_path = None
            if args.out:
                file_path = args.out
            elif os.path.exists(options["data"]):
                file_path = options["data"]
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    if args.csv or options["data"].endswith(".csv"):
                        csv_fields = json_data[0].keys() if json_data else []
                        writer = csv.DictWriter(f, csv_fields)
                        writer.writeheader()
                        writer.writerows(json_data)
                    else:
                        json.dump(json_data, f)
            else:
                raise ValueError(
                    "You have not specified a --out path, I don't know where to save."
                )

        options["callback"] = edit_file

    editjson(**options)
