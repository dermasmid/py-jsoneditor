import jsoneditor
import requests

jsoneditor.editjson(requests.get('https://jsonplaceholder.typicode.com/posts').json())
jsoneditor.editjson(requests.get('https://jsonplaceholder.typicode.com/comments').text)