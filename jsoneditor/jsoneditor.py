import json
import multiprocessing
import webbrowser
import random
import os
import sys
import platform
import re
import requests
import mimetypes
import signal
from typing import Union
from wsgiref.simple_server import make_server, WSGIRequestHandler
from jinja2 import Environment, FileSystemLoader
from multiprocessing import Process, set_start_method


if platform.system() == 'Darwin':
    set_start_method("fork")

# Get installation dir
install_dir = os.path.dirname(os.path.realpath(__file__))


# Gracefull kill for nicer killing of the process
def graceful_kill(x, y):
    for i in multiprocessing.active_children():
        i.terminate()
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, graceful_kill)


# Main logic
def editjson(data: Union[dict, str], callback: callable = None, options: dict = None):

    # Make wsgi handler
    class AltWsgiHandler(WSGIRequestHandler):
        def log_message(self, format, *args):
            pass

    def send_response(status, content_type, respond):
        headers = [('Content-type', content_type)]
        respond(status, headers)
    
    # Get json data
    if type(data) is str:
        try:
            data = json.loads(data)
        except ValueError:
            regex_pattern = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
            url = re.findall(regex_pattern, data)
            if url:
                text_data = requests.get(url[0]).text
                try:
                    data = json.loads(text_data)
                except ValueError:
                    raise ValueError('The url passed did not return valid JSON')
            else:
                raise ValueError('No valid value passed')

    # Server logic
    def wsgi_app(environ, respond):
        path = environ['PATH_INFO']
        method = environ['REQUEST_METHOD']
        file_path = install_dir + path
        j2_env = Environment(loader=FileSystemLoader(install_dir + '/templates'))
        # index.html
        if method == 'GET':
            if path == '/':
                send_response('200 OK', 'text/html', respond)
                html = j2_env.get_template('index.html').render(data=data, send_back_json=bool(callback), options=options)
                yield html.encode('utf-8')
            # Close endpoint
            elif path == '/close':
                send_response('200 OK', 'text/plain', respond)
                yield b''
                os.kill(os.getpid(), 9)
            # Serve static files
            elif path.startswith('/static') and os.path.exists(file_path):
                type = mimetypes.guess_type(file_path)[0]
                send_response('200 OK', type, respond)
                yield open(file_path, "rb").read()
            # 404
            else:
                send_response('404 - Not Found', 'text/plain', respond)
                yield b''
        # callback endpoint
        elif method == 'POST':
            if path == '/callback':
                request_body_size = int(environ['CONTENT_LENGTH'])
                callback_data = json.loads(environ['wsgi.input'].read(request_body_size).decode('utf-8'))['data']
                callback(callback_data)
                send_response('200 OK', 'text/plain', respond)
                yield b''
    
    # Start server
    port = random.randint(1023, 65353)
    server = make_server('', port, wsgi_app, handler_class=AltWsgiHandler)
    process = Process(target=server.serve_forever)
    process.start()
    webbrowser.open(f'http://localhost:{port}/')


# cli function
def main():
    if '-o' in sys.argv:
        sys.argv.remove('-o')
        callback = print
    else:
        callback = None
    if not os.isatty(0):
        data = ''.join(x for x in sys.stdin)
    else:
        if len(sys.argv) == 2:
            data = sys.argv[1]
        else:
            raise Exception('Got invalid number of arguments')

    editjson(data=data, callback=callback)
