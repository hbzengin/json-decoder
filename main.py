import json
import json_decoder
import requests


def main() -> None:
    api_url = "https://api.github.com/repos/python/cpython"

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        raw_json = response.text

        builtin_obj = json.loads(raw_json)  # built-in JSON module
        my_obj = json_decoder.decode(raw_json)  # my decoder

        assert my_obj == builtin_obj  # compare

        print(json.dumps(my_obj, indent=4))

    except AssertionError:
        print("Assertion failed")

    except Exception as e:
        print(f"Error while fetching or decoding JSON: {e}")


if __name__ == "__main__":
    main()
