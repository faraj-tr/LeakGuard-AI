from leakguard.extractor import (
    classify_assignment,
    extract_assignment,
)


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


def test_expression_assignment_is_not_extracted_as_literal():
    result = extract_assignment(
        "password = generate_password()"
    )

    assert result is None


def test_classifies_expression_assignment():
    result = classify_assignment(
        'password = os.getenv("PASSWORD")'
    )

    assert result == {
        "kind": "expression",
        "variable_name": "password",
        "value": None,
    }


def test_extracts_typed_python_assignment():
    result = extract_assignment(
        'password: str = "ABC123XYZ"'
    )

    assert result == {
        "variable_name": "password",
        "value": "ABC123XYZ",
    }


def test_extracts_typed_typescript_assignment():
    result = extract_assignment(
        'const api_key: string = "ABC123XYZ";'
    )

    assert result == {
        "variable_name": "api_key",
        "value": "ABC123XYZ",
    }


def test_extracts_exported_javascript_assignment():
    result = extract_assignment(
        'export const api_key = "ABC123XYZ";'
    )

    assert result == {
        "variable_name": "api_key",
        "value": "ABC123XYZ",
    }


def test_extracts_final_name_from_dotted_target():
    result = extract_assignment(
        'self.password = "ABC123XYZ"'
    )

    assert result == {
        "variable_name": "password",
        "value": "ABC123XYZ",
    }


def test_extracts_yaml_style_quoted_property():
    result = extract_assignment(
        'api_key: "ABC123XYZ"'
    )

    assert result == {
        "variable_name": "api_key",
        "value": "ABC123XYZ",
    }
