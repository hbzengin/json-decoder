# My JSON Decoder in Python

This repository contains an implementation of a JSON decoder in Python. The`JSONDecoder` class parses JSON strings into native Python data structures without relying on the built-in `json` module (except for comparison for correctness in tests). The implementation handles all types that can be part of a valid JSON format: strings, numbers, objects, arrays, booleans, and nulls. If decoding fails due to a invalid raw JSON, `JSONDecodeError` is thrown. The `main.py` file gives a basic example by comparing the output of this decoder against Python's built-in `json.loads`.

### Usage

You can use the decoder in two ways:

```python
from json_decoder import decode
result = decode('{"key": "value"}')
```

Or directly using the `JSONDecoder` class:

```python
from json_decoder import JSONDecoder
decoder = JSONDecoder('{"key": "value"}')
result = decoder.decode()
```

The `tests/` directory includes several tests for correctness, including checks for edge cases. If you make modifications to the source code, you can run `pytest` to verify that the implementation is still correct. Feel free to make contributions to the tests if you think you can come up with other edge cases.
