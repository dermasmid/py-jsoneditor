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

## Build

```bash
python3 setup.py sdist
```
