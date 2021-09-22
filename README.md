# 💥py-jsoneditor💥
Quickly View and Edit any JSON data.


# Why?

When working with JSON data, you offten need to get a structured view of the JSON in order to be able to work with it. There's an online tool [https://jsoneditoronline.org/](https://jsoneditoronline.org/) which i used for this, but copying/pasting all the time got frustrating pretty quickly, This is why i created this package which you can launch right from python or from the command line.


# Screenshot

![](https://res.cloudinary.com/dermasmid/image/upload/v1624745064/Screenshot_from_2021-06-27_01-02-58_qymcrb.png)


# Installation

```bash
pip install jsoneditor
```


# Python example

In python you can simply import `jsoneditor` and call the `editjson` function, the first argument is going to be the data. See [Formats you can pass the JSON as](#formats-you-can-pass-the-json-as) for all the formats you can pass the JSON in. See [Python api](#python-api) for a full list of addtional arguments that you can pass to `editjson`.
```python
import requests
import jsoneditor

data = requests.get('https://jsonplaceholder.typicode.com/comments').json()
jsoneditor.editjson(data)
```


# Command line example

From the command line you can either pass the data as an argument as so:
```bash
jsoneditor '{"Hey": "Hi"}'
```
Or you can pipe it in like so:
```bash
curl https://jsonplaceholder.typicode.com/comments | jsoneditor
```
Or you can use what you have in your clipboard like so:
```bash
jsoneditor -c
```
See [Formats you can pass the JSON as](#formats-you-can-pass-the-json-as) for all the formats you can pass the JSON in.

Refer to [CLI options](#cli-options) for a list of all cli options. Alternatively you can run `jsoneditor --help` from your terminal to see it.


## <a></a>Formats you can pass the JSON as

You can pass the json in any of the following formats:
* as valid json string. Example: `{"Hey": "Hi"}`
* as a python dict. Example: `{'Hey': 'hi'}`
* as a url the points to valid json. Example: `https://jsonplaceholder.typicode.com/comments`
* as a file path that is valid json. Example: `data.json`


## <a></a>Python Api

| parameter | type    | optional  |description                                                                  |
| --------- | ------- | -------- |-----------------------------------------------------------------------------|
| `data`    | `Any`     | ❌ |  The data in any of [these](#formats-you-can-pass-the-json-as) formats.       |
| `callback`| `callable`| ✔️ |  If you provide this argument you will have a ✅ button which will trigger this callback.|
| `options` | `dict`    | ✔️ | Options to pass the the jsoneditor object. See [here](https://github.com/josdejong/jsoneditor/blob/master/docs/api.md#configuration-options)|
| `keep_running`| `bool` | ✔️ | Whether to keep the server running. Defaults to `False`.                 |
| `run_in_thread`| `bool` | ✔️ | Whether to run the server in a separate thread. Defaults to `False`.    |
| `is_csv`| `bool` | ✔️ | Whether the data is csv data. Defaults to `False`.                             |
| `title`| `str` | ✔️ | A title to display in the browser.                                               |
| `port`| `int` | ✔️ | specify which port to use.                                                        |


## <a></a>CLI options

| parameter | description                                                           |
| --------- | ----------------------------------------------------------------------|
| `data`    | The data in any of [these](#formats-you-can-pass-the-json-as) formats.|
| `-o`      | Add a button that will output the json back to the console.           |
| `-b`      | Keep running in backround.                                            |
| `-c`      | Get JSON input from clipboard.                                        |
| `-k`      | Keep alive.                                                           |
| `-e`      | Edit mode.                                                            |
| `-p`      | Server port.                                                          |
| `--out`   | File to output when in edit mode.                                     |
| `-t`      | Title to display in browser window.                                   |
| `--csv`   | Input is CSV.                                                         |


## Build

```bash
python setup.py sdist
```

# Acknowledgements

* [jsoneditor](https://github.com/josdejong/jsoneditor)
