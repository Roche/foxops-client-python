# foxops-client-python

This repository contains the Python client for the [foxops](https://github.com/roche/foxops) templating tool.

## Installation

```shell
pip install foxops-client
```

## Usage

```python
from foxops_client import FoxOpsClient

client = FoxOpsClient("http://localhost:8080", "my-token")
client.list_incarnations()
```
