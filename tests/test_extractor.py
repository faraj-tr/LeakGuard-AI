from leakguard.extractor import extract_assignment


def test_extracts_python_assignment():
    result = extract_assignment(
        'x = "K7mP2xQ9vL4sN8zA1c"'
    )

    assert result == {
        "variable_name": "x",
        "value": "K7mP2xQ9vL4sN8zA1c",
    }


def test_extracts_javascript_const_assignment():
    result = extract_assignment(
        'const apiValue = "ABC123XYZ";'
    )

    assert result == {
        "variable_name": "apiValue",
        "value": "ABC123XYZ",
    }


def test_extracts_json_property():
    result = extract_assignment(
        '"token": "ABC123XYZ"'
    )

    assert result == {
        "variable_name": "token",
        "value": "ABC123XYZ",
    }


def test_ignores_function_call():
    result = extract_assignment(
        'print("Hello world")'
    )

    assert result is None