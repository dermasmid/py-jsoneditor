import sys
import os

sys.path.insert(0, '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1]) + '/jsoneditor')

import jsoneditor
import requests


# Test dict
jsoneditor.editjson(requests.get('https://jsonplaceholder.typicode.com/posts').json())


# Test string
jsoneditor.editjson(requests.get('https://jsonplaceholder.typicode.com/comments').text)

#Test editing
jsoneditor.editjson({'hi': '#466'}, lambda data: print(data), {'colorPicker': True})


# Test urls
jsoneditor.editjson('https://jsonplaceholder.typicode.com/users')
