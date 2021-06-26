# Overview
`jsoneditor` will help you a lot if you are working with API's often.

When you first get data from a endpiont and you want to explore it - you can call the `editjson` function, and you will get a browser window with all the json you passed - right there.

See below:

![](https://res.cloudinary.com/dermasmid/image/upload/v1624745064/Screenshot_from_2021-06-27_01-02-58_qymcrb.png)


# Installation

```bash
pip3 install jsoneditor
```

# Usage

In python:
```python
import requests
import jsoneditor

data = requests.get('https://jsonplaceholder.typicode.com/comments').json()
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

# Credits
* [jsoneditor](https://github.com/josdejong/jsoneditor)
