import pytest
import json
from typing import Any

from json_decoder.decoder import JSONDecoder, JSONDecodeError


def decode_with_my_impl(s: str) -> Any:
    decoder: JSONDecoder = JSONDecoder(s)
    return decoder.decode()


def test_empty_input_raises() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl("")


def test_missing_open_brace() -> None:
    # Only whitespace should raise an error
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl("   ")


def test_simple_empty_object_and_extra_characters() -> None:
    assert decode_with_my_impl("{}") == {}

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl("{} trailing")

    assert decode_with_my_impl("   {  }  ") == {}


def test_simple_key_string_value() -> None:
    s: str = '{"name": "Alice"}'
    my_impl: Any = decode_with_my_impl(s)
    builtin: Any = json.loads(s)
    assert my_impl == builtin

    s2: str = '{"age":30}'
    assert decode_with_my_impl(s2) == json.loads(s2)

    s3: str = '{ "a":1, "b": true, "c": null }'
    assert decode_with_my_impl(s3) == json.loads(s3)


def test_nested_objects() -> None:
    s: str = '''
    {
        "outer": {
            "inner": {
                "x": -5,
                "y": [true, false, null]
            },
            "message": "ok"
        },
        "flag": false
    }
    '''
    assert decode_with_my_impl(s) == json.loads(s)


def test_string_escaped_characters() -> None:
    s: str = r'{"text": "Line1\nLine2\t\\\"End\""}'
    my_impl: Any = decode_with_my_impl(s)
    builtin: Any = json.loads(s)
    assert my_impl == builtin

    s2: str = r'{"u": "\u0041\u00DF"}'
    my_impl2: Any = decode_with_my_impl(s2)
    builtin2: Any = json.loads(s2)
    assert my_impl2 == builtin2

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": "unterminated}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(r'{"a": "\x"}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(r'{"a": "\u00G1"}')


def test_numbers_integers_and_floats() -> None:
    s: str = '{"i1": 0, "i2": -123, "i3": 456}'
    assert decode_with_my_impl(s) == json.loads(s)

    s2: str = '{"f1": 0.0, "f2": -3.14, "f3": 2.71828}'
    assert decode_with_my_impl(s2) == json.loads(s2)

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"bad": 01}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"bad": 3.}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"bad": 12a3}')


def test_boolean_and_null_literals() -> None:
    s: str = '{"t": true, "f": false, "n": null}'
    assert decode_with_my_impl(s) == json.loads(s)

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"bad": truth}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"bad": tru}')


def test_simple_and_nested_arrays() -> None:
    s: str = '{"arr": []}'
    assert decode_with_my_impl(s) == json.loads(s)

    s2: str = '{"arr": [1, "two", false, null, {"x": 5}, [3,4]]}'
    assert decode_with_my_impl(s2) == json.loads(s2)

    s3: str = '{"nested": [[[], []], []]}'
    assert decode_with_my_impl(s3) == json.loads(s3)

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"arr": [1,2,]}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"arr": [1,,2]}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"arr": [@]}')


def test_object_errors_missing_colon_and_trailing_comma() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a" "b"}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": 1')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": 1,}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": 1,, "b": 2}')


def test_missing_value_after_key() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": }')


def test_invalid_value_type() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": &}')


def test_complex_realistic_json() -> None:
    s: str = '''
    {
      "users": [
        {
          "id": 1,
          "name": "John Doe",
          "roles": ["admin","user"],
          "active": true
        },
        {
          "id": 2,
          "name": "Jane \\u0043on",
          "roles": [],
          "active": false
        }
      ],
      "count": 2,
      "next": null
    }
    '''
    assert decode_with_my_impl(s) == json.loads(s)


def test_whitespace_variations_everywhere() -> None:
    s: str = '{ \n\t"a"\t : \n  [\t1 , 2  ,3 ] , "b" : { "x" : true } }  '
    assert decode_with_my_impl(s) == json.loads(s)


def test_deep_nesting_and_large_array() -> None:
    deep: str = '{"a": ' + ('[' * 20) + '1' + (']' * 20) + '}'
    assert decode_with_my_impl(deep) == json.loads(deep)

    large_list: list[int] = list(range(100))
    builtin_obj: dict[str, Any] = {"nums": large_list}
    s2: str = '{"nums": [' + ",".join(str(n) for n in large_list) + ']}'
    assert decode_with_my_impl(s2) == builtin_obj


def test_invalid_json_extra_characters_midway() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a":1 random }')


def test_non_string_key() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{unquoted: 1}')


def test_null_top_level_object() -> None:
    # null is valid JSON at top level
    assert decode_with_my_impl("null") == json.loads("null")

def test_boolean_top_level_allowed() -> None:
    # Booleans are valid JSON at top level
    assert decode_with_my_impl("true") == json.loads("true")
    assert decode_with_my_impl("false") == json.loads("false")

def test_number_top_level_allowed() -> None:
    # Numbers are valid JSON at top level
    assert decode_with_my_impl("123") == json.loads("123")
    assert decode_with_my_impl("-456") == json.loads("-456")
    assert decode_with_my_impl("0.789") == json.loads("0.789")

def test_string_top_level_allowed() -> None:
    # Strings are valid JSON at top level
    assert decode_with_my_impl('"hello"') == json.loads('"hello"')
    assert decode_with_my_impl('""') == json.loads('""')
    assert decode_with_my_impl("\"just a string\"") == json.loads("\"just a string\"")

def test_array_top_level_allowed() -> None:
    # Arrays are valid JSON at top level
    assert decode_with_my_impl("[]") == json.loads("[]")
    assert decode_with_my_impl("[1, 2, 3]") == json.loads("[1, 2, 3]")
    assert decode_with_my_impl('["a", "b"]') == json.loads('["a", "b"]')

def test_unicode_out_of_range_in_escape() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(r'{"x":"\uZZZZ"}')


def test_objects_with_adjacent_double_commas_in_values() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": [1,,2]}')


def test_array_missing_closing_bracket() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": [1, 2}')


def test_number_with_multiple_dots() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": 1.2.3}')


def test_deeply_invalid_syntax() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('@#$%^&*')


def test_array_with_leading_zero_number() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": [01, 2]}')


def test_string_containing_escaped_slash_and_backspace() -> None:
    s: str = r'{"path": "C:\\\\folder\\file.txt", "ctrl": "\b\f"}'
    assert decode_with_my_impl(s) == json.loads(s)

def test_empty_string_key_and_value() -> None:
    # Empty string as a key is valid; its value can also be an empty string
    s = '{"": ""}'
    assert decode_with_my_impl(s) == json.loads(s)

    # Whitespace around empty key/value
    s2 = '{  ""  :   ""   }'
    assert decode_with_my_impl(s2) == json.loads(s2)


def test_string_with_all_escape_sequences() -> None:
    # Combine \b, \f, \n, \r, \t, \\, \/, \"
    s = r'{"escapes": "\b\f\n\r\t\\/\""}'
    my_impl = decode_with_my_impl(s)
    builtin = json.loads(s)
    assert my_impl == builtin


def test_unicode_4hex_escape_and_combined_characters() -> None:
    # 4‐hex escapes: \u0041 is 'A'; also mixing literal Unicode
    s = '{"letter": "\\u0041", "cyrillic": "Ч"}'
    my_impl = decode_with_my_impl(s)
    builtin = json.loads(s)
    assert my_impl == builtin


def test_number_fraction_and_zero_prefix() -> None:
    # Valid fractional number with leading zero
    s = '{"frac": 0.001, "neg_frac": -0.010}'
    my_impl = decode_with_my_impl(s)
    builtin = json.loads(s)
    assert my_impl == builtin

    # Invalid: leading dot not allowed
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"bad": .1}')

    # Invalid: trailing dot in number (no digits after)
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"bad": 5.}')

    # Invalid: multiple dots
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"bad": 1.2.3}')


def test_number_scientific_notation_not_supported() -> None:
    # The my_impl parser does not support 'e' or 'E' exponents—should raise
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"exp": 1e10}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"exp": -2E-5}')


def test_array_with_mixed_whitespace_and_types() -> None:
    s = '{   "mixed": [  123  ,   "hello"   ,null,  [true,false ],  { "k": 0 }  ]  }'
    my_impl = decode_with_my_impl(s)
    builtin = json.loads(s)
    assert my_impl == builtin

    # Array with only whitespace and then closing bracket is valid
    s2 = '{"emptyArr": [   ]}'
    assert decode_with_my_impl(s2) == json.loads(s2)


def test_nested_empty_objects_and_arrays_deep() -> None:
    # 5 levels of nested objects, each containing a key "b" whose value is
    # 5 levels of nested empty arrays. Total depth: {"a": {"b": {"b": {"b": {"b": [[[[[]]]]]}}}}}
    deep = (
        '{"a": '
          + '{"b": ' * 5
          + '[' * 5
          + ']' * 5
          + '}' * 5
        + '}'
    )
    
    # Just verify that your decoder matches json.loads - that's the real test!
    expected = json.loads(deep)
    result = decode_with_my_impl(deep)
    assert result == expected

def test_object_with_many_keys_and_varied_types() -> None:
    # Create an object with 50 keys programmatically
    pairs: list[str] = []
    for i in range(50):
        value: Any
        if i % 5 == 0:
            value = "string" + str(i)
        elif i % 5 == 1:
            value = i
        elif i % 5 == 2:
            value = True
        elif i % 5 == 3:
            value = None
        else:
            value = [i, {"nested": i * 2}]
        # For strings, wrap in quotes; for others, rely on json.dumps
        if isinstance(value, str):
            pairs.append(f'"key{i}": "{value}"')
        else:
            pairs.append(f'"key{i}": {json.dumps(value)}')
    body = "{ " + ", ".join(pairs) + " }"
    my_impl = decode_with_my_impl(body)
    builtin = json.loads(body)
    assert my_impl == builtin



def test_invalid_literals_and_wrong_keyword() -> None:
    # 'Truth' is not a valid literal
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": Truth}')

    # Partial 'nul' without 'l'
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": nu}')

    # Random letters where value expected
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": abc}')


def test_object_missing_quotes_around_key() -> None:
    # Key must be in double quotes
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{foo: 1}')

    # Single quotes not allowed
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl("{'a': 1}")


def test_array_errors_extra_commas_and_missing_commas() -> None:
    # Double commas in array
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"arr": [1,,2]}')

    # Missing comma between elements
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"arr": [1 2]}')

    # Trailing comma before bracket
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"arr": [1,2,]}')


def test_unescaped_control_in_string_is_error() -> None:
    # A literal newline in a JSON string is invalid
    s = "{\n\"a\": \"line1\nline2\"}"
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(s)


def test_multiple_branches_of_malformed_input() -> None:
    # Completely invalid JSON
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('@#$%^&*')

    # Missing colon
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a" 1}')

    # Missing closing quote in key
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a: 1}')

    # Missing comma between key/value pairs
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": 1 "b": 2}')

    # Unexpected character after object close
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": 1}}')


def test_large_integer_values() -> None:
    # JSON allows arbitrarily large integers; my_impl uses Python int, so it should work
    large = 10 ** 30
    s = f'{{"big": {large}}}'
    my_impl = decode_with_my_impl(s)
    builtin = json.loads(s)
    assert my_impl == builtin


def test_mixed_deep_structure_combined() -> None:
    s = '''
    {
      "users": [
        {"id": 1, "name": "A", "prefs": {"langs": ["py","js"], "active": true}},
        {"id": 2, "name": "B", "prefs": {"langs": [], "active": false}}
      ],
      "meta": {"count": 2, "description": null},
      "values": [1, 2.5, {"nestedArr": [[], [3]]}, []]
    }
    '''
    my_impl = decode_with_my_impl(s)
    builtin = json.loads(s)
    assert my_impl == builtin

def test_extreme_nesting_depth() -> None:
   # Test very deep nesting (100 levels)
   deep_array = '{"data": ' + '[' * 100 + '42' + ']' * 100 + '}'
   assert decode_with_my_impl(deep_array) == json.loads(deep_array)
   
   deep_object = '{"level": ' + '{"next": ' * 50 + 'null' + '}' * 50 + '}'
   assert decode_with_my_impl(deep_object) == json.loads(deep_object)


def test_edge_case_numbers() -> None:
   # Test various number formats
   s = '{"zero": 0, "negative_zero": -0, "large": 999999999999999999, "small": -999999999999999999}'
   assert decode_with_my_impl(s) == json.loads(s)
   
   # Test decimal numbers
   s2 = '{"decimals": [0.0, -0.0, 123.456, -123.456, 0.000001]}'
   assert decode_with_my_impl(s2) == json.loads(s2)
   
   # Invalid number formats
   with pytest.raises(JSONDecodeError):
       decode_with_my_impl('{"bad": +123}')  # Leading + not allowed
   
   with pytest.raises(JSONDecodeError):
       decode_with_my_impl('{"bad": 00123}')  # Multiple leading zeros


def test_complex_string_escapes() -> None:
   # Test all escape sequences together
   s = r'{"complex": "\"\\\b\f\n\r\t\/\u0048\u0065\u006c\u006c\u006f"}'
   assert decode_with_my_impl(s) == json.loads(s)
   
   # Test unicode with various ranges
   s2 = '{"unicode": "\\u0000\\u001F\\u0020\\u007F\\u0080\\u00FF\\uFFFF"}'
   assert decode_with_my_impl(s2) == json.loads(s2)
   
   # Invalid unicode escapes
   with pytest.raises(JSONDecodeError):
       decode_with_my_impl('{"bad": "\\uGGGG"}')
   
   with pytest.raises(JSONDecodeError):
       decode_with_my_impl('{"bad": "\\u123"}')  # Only 3 hex digits


def test_whitespace_edge_cases() -> None:
   # Test all types of whitespace
   whitespaces = [' ', '\t', '\n', '\r']
   for ws in whitespaces:
       s = f'{{{ws}"key"{ws}:{ws}"value"{ws}}}'
       assert decode_with_my_impl(s) == json.loads(s)
   
   # Mixed whitespace
   s = '{\n\t  "mixed"  \r\n:\t\t[\n   1,\r2   ,\t\n3\r\n]\n}'
   assert decode_with_my_impl(s) == json.loads(s)


def test_empty_containers_variations() -> None:
   # Various empty container patterns
   test_cases = [
       '{}',
       '{"empty_obj": {}}',
       '{"empty_arr": []}',
       '{"nested_empty": {"inner": {}}}',
       '{"mixed": [[], {}, [], {}]}',
       '{"deep_empty": [[[[{}]]]]}',
   ]
   
   for case in test_cases:
       assert decode_with_my_impl(case) == json.loads(case)


def test_string_boundary_cases() -> None:
   # Empty strings
   s = '{"empty": "", "also_empty": ""}'
   assert decode_with_my_impl(s) == json.loads(s)
   
   # Very long string
   long_str = "a" * 10000
   s2 = f'{{"long": "{long_str}"}}'
   assert decode_with_my_impl(s2) == json.loads(s2)
   
   # String with only escaped characters
   s3 = r'{"escaped": "\"\\\b\f\n\r\t"}'
   assert decode_with_my_impl(s3) == json.loads(s3)


def test_array_edge_cases() -> None:
   # Single element arrays
   test_cases = [
       '{"arr": [1]}',
       '{"arr": ["single"]}',
       '{"arr": [true]}',
       '{"arr": [null]}',
       '{"arr": [{}]}',
       '{"arr": [[]]}',
   ]
   
   for case in test_cases:
       assert decode_with_my_impl(case) == json.loads(case)
   
   # Large arrays
   large_array = '[' + ','.join(str(i) for i in range(1000)) + ']'
   s = f'{{"numbers": {large_array}}}'
   assert decode_with_my_impl(s) == json.loads(s)


def test_object_key_variations() -> None:
   # Various valid key formats
   test_cases = [
       '{"": "empty_key"}',  # Empty string key
       '{"a": 1, "b": 2, "c": 3}',  # Multiple keys
       '{"key with spaces": "value"}',
       '{"key\\nwith\\tescapes": "value"}',
       '{"\\u0048\\u0065\\u006c\\u006c\\u006f": "unicode_key"}',
   ]
   
   for case in test_cases:
       assert decode_with_my_impl(case) == json.loads(case)


def test_mixed_type_arrays() -> None:
   # Arrays with all possible value types
   s = '{"mixed": [null, true, false, 0, -1, 1.5, "", "string", [], {}, {"nested": [1,2,3]}]}'
   assert decode_with_my_impl(s) == json.loads(s)
   
   # Nested mixed arrays
   s2 = '{"nested_mixed": [[null, true], [false, 0], [-1, 1.5], ["", "string"], [[], {}]]}'
   assert decode_with_my_impl(s2) == json.loads(s2)


def test_error_recovery_boundaries() -> None:
   # Test errors at different parsing stages
   error_cases = [
       '',  # Empty input
       '{',  # Unclosed object
       '{"key"',  # Missing colon and value
       '{"key":',  # Missing value
       '{"key": "value"',  # Missing closing brace
       '{"key": "value",',  # Trailing comma
       '{"key": "value", "key2"',  # Second key missing colon
       '[',  # Unclosed array
       '[1',  # Missing closing bracket
       '[1,',  # Trailing comma in array
       '[1,,2]',  # Double comma
       '{"key": [}',  # Mismatched brackets
       '{"key": ]}',  # Wrong closing bracket
   ]
   
   for case in error_cases:
       with pytest.raises(JSONDecodeError):
           decode_with_my_impl(case)


def test_literal_parsing_edge_cases() -> None:
   # Test literal parsing with various contexts
   s = '{"literals": [true, false, null, true, false, null]}'
   assert decode_with_my_impl(s) == json.loads(s)
   
   # Literals as object values
   s2 = '{"t": true, "f": false, "n": null, "t2": true, "f2": false, "n2": null}'
   assert decode_with_my_impl(s2) == json.loads(s2)
   
   # Invalid literal variations
   invalid_literals = [
       '{"bad": True}',  # Wrong capitalization
       '{"bad": FALSE}',  # Wrong capitalization
       '{"bad": NULL}',  # Wrong capitalization
       '{"bad": tru}',  # Incomplete
       '{"bad": fals}',  # Incomplete
       '{"bad": nul}',  # Incomplete
       '{"bad": truex}',  # Extra characters
       '{"bad": falsex}',  # Extra characters
       '{"bad": nullx}',  # Extra characters
   ]
   
   for case in invalid_literals:
       with pytest.raises(JSONDecodeError):
           decode_with_my_impl(case)


def test_number_precision_and_range() -> None:
   # Test floating point precision
   s = '{"precise": [0.1, 0.2, 0.3, 0.123456789, 123.456789]}'
   assert decode_with_my_impl(s) == json.loads(s)
   
   # Very small and large numbers
   s2 = '{"range": [0.000000001, 999999999.999999999, -999999999.999999999]}'
   assert decode_with_my_impl(s2) == json.loads(s2)


def test_structure_variations() -> None:
   # Object in array in object pattern
   s = '{"data": [{"users": [{"id": 1, "tags": ["a", "b"]}]}]}'
   assert decode_with_my_impl(s) == json.loads(s)
   
   # Array in object in array pattern
   s2 = '[{"items": [1, 2, {"nested": [3, 4]}]}, {"items": []}]'
   assert decode_with_my_impl(s2) == json.loads(s2)
   
   # Alternating structures
   s3 = '{"a": [{"b": [{"c": {"d": [1]}}]}]}'
   assert decode_with_my_impl(s3) == json.loads(s3)


def test_stress_test_large_structure() -> None:
    # Generate a large, complex JSON structure
    def generate_nested_structure(depth: int, width: int) -> str:
        if depth == 0:
            return str(depth)
        
        items: list[str] = []  # Explicitly type the list
        for i in range(width):
            if i % 3 == 0:
                items.append(f'"key{i}": {generate_nested_structure(depth-1, width)}')
            elif i % 3 == 1:
                items.append(f'"key{i}": [{generate_nested_structure(depth-1, width)}]')
            else:
                items.append(f'"key{i}": "value{i}"')
        
        return '{' + ', '.join(items) + '}'
    
    # Generate moderately complex structure
    complex_json = generate_nested_structure(4, 3)
    assert decode_with_my_impl(complex_json) == json.loads(complex_json)


def test_pathological_cases() -> None:
   # Deeply nested alternating structures
   alternating = '{"a": [{"b": [{"c": [{"d": {}}]}]}]}'
   assert decode_with_my_impl(alternating) == json.loads(alternating)
   
   # Many keys in single object
   many_keys = '{' + ', '.join(f'"key{i}": {i}' for i in range(100)) + '}'
   assert decode_with_my_impl(many_keys) == json.loads(many_keys)
   
   # Long array of varied types
   long_mixed = '{"data": [' + ', '.join([
       'null', 'true', 'false', '42', '"string"', '[]', '{}'
   ] * 50) + ']}'
   assert decode_with_my_impl(long_mixed) == json.loads(long_mixed)

def test_duplicate_keys_overwrite_behavior() -> None:
    # JSON with duplicate keys should keep the last value
    s = '{"a": 1, "b": 2, "a": 3}'
    # json.loads will return {"a": 3, "b": 2}
    expected = json.loads(s)
    result = decode_with_my_impl(s)
    assert result == expected
    assert result["a"] == 3
    assert result["b"] == 2


def test_invalid_leading_plus_in_number() -> None:
    # A leading plus sign is not allowed in JSON numbers
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"plus": +5}')


def test_lonely_minus_sign_is_invalid() -> None:
    # A minus sign without digits is invalid
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('"-": -')


def test_nonbreaking_space_instead_of_whitespace() -> None:
    # U+00A0 (non-breaking space) is not recognized as whitespace by the parser
    # json.loads also errors on this
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{\u00A0"a": 1}')


def test_literal_tab_in_string_is_error() -> None:
    # A literal tab character inside a JSON string must be escaped (\t). Unescaped is invalid.
    s = "{ \"a\": \"line1\tline2\" }"
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(s)


def test_unescaped_backspace_literal_in_string_is_error() -> None:
    # A literal backspace (0x08) in a string is disallowed
    # Represented here with Python's \b in a raw literal
    s = "{ \"a\": \"bad\bchar\" }"
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(s)


def test_escaped_slash_and_unescaped_slash_in_string() -> None:
    # A forward slash (/) does not have to be escaped, but if escaped (\/) it should parse as '/'
    s = r'{"path1": "/usr/bin", "path2": "\/usr\/local"}'
    expected = json.loads(s)
    result = decode_with_my_impl(s)
    assert result == expected
    assert result["path1"] == "/usr/bin"
    assert result["path2"] == "/usr/local"


def test_short_unicode_escape_length() -> None:
    # \u must be followed by exactly 4 hex digits. Here only 2 are provided before a valid sequence,
    # but that still fails because it takes exactly 4 and then sees a second \u
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(r'{"bad": "\u12"}')


def test_object_with_unquoted_true_false_null_as_keys() -> None:
    # Keys must be double-quoted strings; using literals as keys is invalid
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{true: 1}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{false: 2}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{null: 3}')


def test_array_with_malformed_values_and_extra_brackets() -> None:
    # Missing comma between elements
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('[1 2 3]')

    # Extra closing bracket at the end
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('[1,2,3]]')

    # Missing value (nothing between commas)
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('[1,,3]')

    # Values out of order: expecting value but got a brace
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('[{]')


def test_top_level_array_missing_comma() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('[1 2, 3]')


def test_number_with_leading_zeros_and_decimal() -> None:
    # JSON disallows numbers like 000, 00.1, etc.
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"bad": 00}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"bad": 00.1}')

    # But 0.01 is valid
    s = '{"ok": 0.01}'
    assert decode_with_my_impl(s) == json.loads(s)


def test_boolean_literal_as_top_level_with_whitespace() -> None:
    # Leading/trailing whitespace around a top-level boolean
    assert decode_with_my_impl('   true   ') is True
    assert decode_with_my_impl('\nfalse\r\n') is False


def test_null_literal_as_top_level_with_extra_brackets_error() -> None:
    # "null" is valid alone, but "null[]" is invalid
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('null[]')


def test_complex_mixed_key_names_with_escapes() -> None:
    # Keys that include a mixture of escaped characters and Unicode must parse correctly
    s = r'{"newline\nkey": "value1", "quote\"key": "value2", "\u0046\u006f\u006f": "Foo"}'
    expected = json.loads(s)
    result = decode_with_my_impl(s)
    assert result == expected
    assert result["newline\nkey"] == "value1"
    assert result['quote"key'] == "value2"
    assert result["Foo"] == "Foo"


def test_array_of_only_commas_is_invalid() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('[,,,]')


def test_string_with_escape_at_end_of_input() -> None:
    # A trailing backslash with no escape target should error
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(r'{"a": "incomplete_escape\"}')

def test_string_ending_with_backslash_followed_by_more_content() -> None:
    # String ends with incomplete escape, but there's more JSON after the closing quote
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(r'{"a": "incomplete\", "b": "valid"}')
    
    # String ends with incomplete escape, followed by another key-value pair
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(r'{"first": "ends_with\", "second": 42}')
    
    # String ends with incomplete escape, followed by array
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(r'{"text": "trailing\", "numbers": [1, 2, 3]}')
    
    # String ends with incomplete escape in an array
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(r'["valid", "incomplete\", "another"]')


def test_number_followed_by_letter_mid_json_error() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"n": 123abc}')


def test_object_with_misplaced_brace_and_bracket() -> None:
    # Mismatched closing tokens
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": [1, 2]} }')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"a": {1, 2}}')  # braces used instead of bracket inside object


def test_valid_top_level_string_with_escaped_characters() -> None:
    s = r'"This is a \"top-level\" string with \u263A"'
    assert decode_with_my_impl(s) == json.loads(s)


def test_float_with_no_leading_zero_and_zero_fraction_allowed_false() -> None:
    # .5 is invalid; 0.5 is valid; "0." is invalid
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"f": .5}')

    assert decode_with_my_impl('{"f": 0.5}') == json.loads('{"f": 0.5}')

    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('{"f": 1.}')


def test_array_with_only_whitespace_and_commas_error() -> None:
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl('[   ,   ,   ]')


def test_long_string_with_embedded_surrogates_and_literals() -> None:
    # A long string mixing literal Unicode characters and surrogate-escaped sequences
    literal_unicode = "漢字テスト" * 100
    s = '{"long": "' + literal_unicode + r'\u4E00\u4E8C\u4E09' + '"}'
    expected = json.loads(s)
    result = decode_with_my_impl(s)
    assert result == expected
    assert literal_unicode in result["long"]


def test_object_key_with_control_characters_error() -> None:
    # Keys cannot contain unescaped control characters (like a literal newline)
    s = "{\n\"bad\nkey\": 1}"
    with pytest.raises(JSONDecodeError):
        decode_with_my_impl(s)