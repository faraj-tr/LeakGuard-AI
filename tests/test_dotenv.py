from leakguard.dotenv import extract_dotenv_assignment


def test_extracts_unquoted_dotenv_value():
    result = extract_dotenv_assignment(
        "VITE_API_KEY=ABC123XYZ"
    )

    assert result == {
        "variable_name": "VITE_API_KEY",
        "value": "ABC123XYZ",
    }


def test_extracts_double_quoted_dotenv_value():
    result = extract_dotenv_assignment(
        'API_KEY="ABC123XYZ"'
    )

    assert result == {
        "variable_name": "API_KEY",
        "value": "ABC123XYZ",
    }


def test_ignores_dotenv_comment():
    result = extract_dotenv_assignment(
        "# API_KEY=ABC123XYZ"
    )

    assert result is None


def test_ignores_empty_dotenv_line():
    result = extract_dotenv_assignment("")

    assert result is None