# Installation

```bash
pip3 install jsoneditor
```

# Usage

In python:
```python
import requests
import jsoneditor

data = requests.get('your endpiont here').json()
jsoneditor.editjson(data)
```
From the terminal:

You got a cuple of options.

1. `python -m jsoneditor '{"Hey": "Hi"}'`
2. `curl https://jsonplaceholder.typicode.com/comments | jsoneditor`
3. `jsoneditor '{"Hey": "Hi"}'`

## Forms of passing the json

You can pass the json in any of the following forms:
* as valid json string
* as a python dict
* as a url the points to valid json
* as a file path that is valid json

## Build

```bash
python3 setup.py sdist
```
