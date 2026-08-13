import re


DOTENV_ASSIGNMENT_PATTERN = re.compile(
    r"""
    ^\s*

    # Environment variable name
    (?P<variable>[A-Za-z_][A-Za-z0-9_]*)

    \s*=\s*

    # Entire raw value
    (?P<value>.*?)

    \s*$
    """,
    re.VERBOSE,
)


def extract_dotenv_assignment(line: str) -> dict | None:
    """
    Extract a variable name and value from a .env line.

    Examples:
        API_KEY=ABC123
        API_KEY="ABC123"
        API_KEY='ABC123'

    Empty lines and comments are ignored.
    """

    stripped_line = line.strip()

    if not stripped_line:
        return None

    if stripped_line.startswith("#"):
        return None

    match = DOTENV_ASSIGNMENT_PATTERN.match(line)

    if not match:
        return None

    variable_name = match.group("variable")

    value = match.group("value").strip()

    # Remove matching surrounding quotes.
    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in {'"', "'"}
    ):
        value = value[1:-1]

    return {
        "variable_name": variable_name,
        "value": value,
    }