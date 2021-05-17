import sys
import os
import platform

if platform.system() == 'Windows':
    separator = '\\'
else:
    separator = '/'

sys.path.insert(0, '/'.join(os.path.dirname(os.path.realpath(__file__)).split(separator)[:-1]) + '/jsoneditor')

import jsoneditor
import requests



if __name__ == '__main__':
    # for testing on linux for win/mac uncomment the next line
    # set_start_method('spawn')

    # Test dict
    jsoneditor.editjson(requests.get('https://jsonplaceholder.typicode.com/posts').json())


    # Test string
    jsoneditor.editjson(requests.get('https://jsonplaceholder.typicode.com/comments').text)


    # Test editing
    jsoneditor.editjson({'hi': '#466'}, print, {'colorPicker': True})


    # Test urls
    jsoneditor.editjson('https://jsonplaceholder.typicode.com/users')
