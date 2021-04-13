import sys
sys.path.append('../jsoneditor')

import jsoneditor
import requests

jsoneditor.editjson(requests.get('https://jsonplaceholder.typicode.com/posts').json())
jsoneditor.editjson(requests.get('https://jsonplaceholder.typicode.com/comments').text)


# Test editing
jsoneditor.editjson({'hi': '#466'}, lambda data: print(data), {'colorPicker': True})