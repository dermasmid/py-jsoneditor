# Installation

```bash
pip3 install jsoneditor
```

# Usage

```python
import requests
import jsoneditor

data = requests.get('your endpiont here').json()
jsoneditor.editjson(data)
```
