"""
Test fixtures for error samples.

Provides sample error messages for testing.
"""

PYTHON_NAME_ERROR = """Traceback (most recent call last):
  File "main.py", line 10, in <module>
    result = calculate_total(items)
  File "calculator.py", line 5, in calculate_total
    return sum(proces for item in items)
NameError: name 'proces' is not defined"""

PYTHON_TYPE_ERROR = """Traceback (most recent call last):
  File "app.py", line 25, in process_data
    result = data + 10
TypeError: can only concatenate str (not "int") to str"""

PYTHON_IMPORT_ERROR = """Traceback (most recent call last):
  File "run.py", line 1, in <module>
    from utils import helper
  File "utils/__init__.py", line 3, in <module>
    from .missing_module import function
ModuleNotFoundError: No module named 'utils.missing_module'"""

PYTHON_ATTRIBUTE_ERROR = """Traceback (most recent call last):
  File "service.py", line 42, in fetch_data
    response.json_data()
AttributeError: 'Response' object has no attribute 'json_data'. Did you mean: 'json'?"""

PYTHON_KEY_ERROR = """Traceback (most recent call last):
  File "config.py", line 15, in get_setting
    return settings['databse_url']
KeyError: 'databse_url'"""

PYTHON_INDEX_ERROR = """Traceback (most recent call last):
  File "processor.py", line 8, in get_item
    return items[10]
IndexError: list index out of range"""

PYTHON_VALUE_ERROR = """Traceback (most recent call last):
  File "converter.py", line 12, in convert
    number = int("not_a_number")
ValueError: invalid literal for int() with base 10: 'not_a_number'"""

PYTHON_SYNTAX_ERROR = """File "broken.py", line 5
    if condition
                ^
SyntaxError: expected ':'"""

ALL_ERRORS = [
    ("NameError", PYTHON_NAME_ERROR),
    ("TypeError", PYTHON_TYPE_ERROR),
    ("ImportError", PYTHON_IMPORT_ERROR),
    ("AttributeError", PYTHON_ATTRIBUTE_ERROR),
    ("KeyError", PYTHON_KEY_ERROR),
    ("IndexError", PYTHON_INDEX_ERROR),
    ("ValueError", PYTHON_VALUE_ERROR),
    ("SyntaxError", PYTHON_SYNTAX_ERROR),
]
