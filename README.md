# foxops-client-python

This repository contains the Python client for the [foxops](https://github.com/roche/foxops) templating tool.

## Installation

```shell
pip install foxops-client
```

## Usage

```python
from foxops_client import FoxopsClient, AsyncFoxopsClient

client = FoxopsClient("http://localhost:8080", "my-token")
incarnations = client.list_incarnations()

# or alternatively, the async version
client = AsyncFoxopsClient("http://localhost:8080", "my-token")
incarnations = await client.list_incarnations()
```
