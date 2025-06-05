from typing import Any, List, Dict


# Run to decode any raw string
def decode(content: str) -> Any | None:
    decoder = JSONDecoder(content)
    return decoder.decode()


# Error thrown when decoding fails
class JSONDecodeError(Exception):
    """Raised when JSON parsing fails due to invalid JSON"""


class JSONDecoder:
    def __init__(self, text: str) -> None:
        self.idx: int = -1  # current index
        self.content: str = text  # raw content
        self.n: int = len(text)  # length of text

    def decode(self) -> Any | None:
        """
        Parse the given JSON string. Return None if error occurs.
        Returns JSONDecodeError if invalid JSON syntax.
        """

        self._skip_whitespace()
        result = self._parse_one()
        self._skip_whitespace()

        char = self._peek()
        if char is not None:
            raise JSONDecodeError("Extra characters after JSON")

        return result

    # Parse one element
    def _parse_one(self) -> Any:
        first = self._peek()

        if first is None:
            raise JSONDecodeError("No input")

        # Important gotcha - JSON doesn't have to start with an object!
        if first == "{":
            return self._parse_object()
        elif first == "[":
            return self._parse_array()
        elif first == '"':
            return self._parse_string()
        elif first in ("t", "f", "n"):
            return self._parse_literal()
        elif first == "-" or first.isdigit():
            return self._parse_number()
        else:
            raise JSONDecodeError("Invalid JSON")

    # See next character (without incrementing index)
    def _peek(self) -> str | None:
        return self.content[self.idx + 1] if (self.idx + 1) < self.n else None

    # Get next character, increment index
    def _next(self) -> str | None:
        char = self._peek()
        if char is not None:
            self.idx += 1
        return char

    # Skip all whitespace characters starting at current index
    def _skip_whitespace(self) -> None:
        while True:
            char = self._peek()
            if char is not None and char in (" ", "\t", "\n", "\r"):
                char = self._next()
            else:
                break

    # Parse a JSON object
    def _parse_object(self) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        self._next()  # consume "{"

        while True:
            self._skip_whitespace()
            char = self._peek()  # must be either end or key
            if char is None:
                raise JSONDecodeError("Object ends without }")
            elif char == "}":
                self._next()
                break
            elif char != '"':
                raise JSONDecodeError("Keys must be strings")

            key = self._parse_string()
            self._skip_whitespace()

            # Got the key, next one must be ":"
            char = self._next()
            if char is None or char != ":":
                raise JSONDecodeError('Key not followed by ":"')

            self._skip_whitespace()
            value = self._parse_one()
            obj[key] = value
            self._skip_whitespace()

            char = self._peek()
            if char == ",":
                self._next()  # consume this comma
                self._skip_whitespace()  # consume possible whitespace
                char = self._peek()
                if char == ",":
                    raise JSONDecodeError("Can't have two commas back to back")
                elif char == "}":
                    raise JSONDecodeError("Can't end with a trailing comma")
            elif (
                char != "}"
            ):  # if not comma, must be closing bracket, another key cant come without ,
                raise JSONDecodeError("Keys must be separated by , ")

        return obj

    # Valid escape characters that can be exist in a string in a JSON object
    _ESCAPE_CHARACTERS: Dict[str, str] = {
        '"': '"',
        "\\": "\\",
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "b": "\b",
        "f": "\f",
        "/": "/",
    }

    # Parse a string
    def _parse_string(self) -> str:
        s = ""
        self._next()  # consume "
        char = self._next()

        while True:
            if char is None:
                raise JSONDecodeError("Unterminated string")

            # Crazy gotcha. I didn't know "\n" and a literal newline were different things.
            if ord(char) < 0x20:
                raise JSONDecodeError("Unescaped control character in string")

            if char == '"':
                break
            elif char == "\\":
                next = self._next()
                if next is None:
                    raise JSONDecodeError("\\ not followed by anything to escape")

                if next == "u":
                    hex_digits = ""
                    for _ in range(4):
                        hd = self._next()
                        if hd is None or not (hd.isdigit() or hd.lower() in "abcdef"):
                            raise JSONDecodeError("Invalid escape with \\u")

                        hex_digits += hd

                    s += chr(int(hex_digits, base=16))
                else:
                    try:
                        s += self._ESCAPE_CHARACTERS[next]
                    except:
                        raise JSONDecodeError("Invalid escape")

            else:
                s += char

            char = self._next()

        return s

    # Parse a number
    def _parse_number(self) -> int | float:
        s = ""
        isFloat = False

        while True:
            char = self._peek()
            if char is not None and not char.isspace() and char not in (",", "}", "]"):
                if char == ".":
                    isFloat = True
                s += char
                self._next()
            else:
                break

        num: int | float = 0

        # s[0] case is handled in the value parsing
        if s[-1] == ".":
            raise JSONDecodeError("Dot cannot be in the end")

        if len(s) >= 2 and s[0] == "0" and s[1].isnumeric():
            raise JSONDecodeError("Number cannot begin with 0")

        try:
            if isFloat:
                num = float(s)
            else:
                num = int(s)
        except:
            raise JSONDecodeError("Invalid number")

        return num

    # Parse an array (of potentially different elements)
    def _parse_array(self) -> List[Any]:
        # if here, first char must be "["
        # array elements can be anything
        char = self._next()  # consume '['
        arr: List[Any] = []
        element: Any = None

        while True:
            self._skip_whitespace()
            char = self._peek()  # handler must consume, so only peek here
            if char is None:
                raise JSONDecodeError("Array ends without ]")
            if char == "]":
                self._next()  # consume ']'
                break

            element = self._parse_one()
            self._skip_whitespace()

            char = self._peek()
            if char == ",":
                self._next()  # consume this comma
                self._skip_whitespace()  # consume possible whitespace after comma
                char = self._peek()
                if char == ",":
                    raise JSONDecodeError("Can't have two commas back to back")
                elif char == "]":
                    raise JSONDecodeError("Can't end with a trailing comma")
                # the case where it's None so JSON ends without a '}'
                # is handled in the next iteration so that is OK
            elif (
                char != "]"
            ):  # if not comma, must be closing bracket, another element cant come
                raise JSONDecodeError("Array elements must be separated with ,")

            arr.append(element)

        return arr

    # Parse "true", "false", or "null"
    def _parse_literal(self) -> bool | None:
        # if here, first letter must be "t", "f", or "n"
        s = ""

        while True:
            char = self._peek()
            if char is not None and not char.isspace() and char not in (",", "}", "]"):
                s += char
                self._next()
            else:
                break

        if s == "true":
            return True
        elif s == "false":
            return False
        elif s == "null":
            return None
        else:
            raise JSONDecodeError("Invalid literal syntax")
