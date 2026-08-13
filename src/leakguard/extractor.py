import re


CODE_ASSIGNMENT_PATTERN = re.compile(
    r"""
    ^\s*

    # Optional JavaScript / TypeScript declaration
    (?:(?:const|let|var)\s+)?

    # Variable name
    (?P<variable>[A-Za-z_][A-Za-z0-9_]*)

    # Assignment operator
    \s*=\s*

    # Quoted value
    (?P<quote>["'])
    (?P<value>[^"']*)
    (?P=quote)

    # Optional JavaScript semicolon
    \s*;?\s*$

    """,
    re.VERBOSE,
)


JSON_ASSIGNMENT_PATTERN = re.compile(
    r"""
    ^\s*

    # JSON-style property name
    ["']
    (?P<variable>[A-Za-z_][A-Za-z0-9_-]*)
    ["']

    \s*:\s*

    # Quoted value
    (?P<quote>["'])
    (?P<value>[^"']*)
    (?P=quote)

    \s*,?\s*$

    """,
    re.VERBOSE,
)


ASSIGNMENT_PATTERNS = [
    CODE_ASSIGNMENT_PATTERN,
    JSON_ASSIGNMENT_PATTERN,
]


def extract_assignment(line: str) -> dict | None:
    """
    Extract a variable name and string value
    from a simple source-code assignment.

    Returns None when the line is not
    a supported assignment.
    """

    for pattern in ASSIGNMENT_PATTERNS:
        match = pattern.match(line)

        if not match:
            continue

        return {
            "variable_name": match.group("variable"),
            "value": match.group("value"),
        }

    return None