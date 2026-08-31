# opcua-test-lab

A personal practice project for learning test automation.

It runs a small OPC UA server (built with [asyncua](https://github.com/FreeOpcUa/opcua-asyncio))
and uses pytest to test it

## Setup

```
pip install -r requirements.txt
```

## Run the server

```
py src/server_methods.py
```

## Run the tests

```
pytest tests/test_*.py
```
