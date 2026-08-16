import re


PASSWORD_VARIABLE_PATTERN = re.compile(
    r"""
    ^
    (?:
        [A-Za-z0-9]+[_-]
    )*
    (?:
        password
        |
        passwd
        |
        pwd
    )
    $
    """,
    re.VERBOSE | re.IGNORECASE,
)


API_KEY_VARIABLE_PATTERN = re.compile(
    r"""
    ^
    (?:
        [A-Za-z0-9]+[_-]
    )*
    (?:
        api[_-]?key
        |
        secret[_-]?key
        |
        client[_-]?secret
        |
        access[_-]?token
        |
        auth[_-]?token
    )
    $
    """,
    re.VERBOSE | re.IGNORECASE,
)


ASSIGNMENT_SECRET_PATTERNS = [
    {
        "name": "Hardcoded Password",
        "severity": "HIGH",
        "variable_pattern": (
            PASSWORD_VARIABLE_PATTERN
        ),
        "value_pattern": re.compile(
            r"^[^\s#]{6,}$"
        ),

        # Raw fallback is retained for
        # non-code configuration formats.
        "pattern": re.compile(
            r"""(?ix)
            \b
            (?:[A-Za-z0-9]+[_-])*
            (?:password|passwd|pwd)
            \b
            \s*[:=]\s*
            ["']?
            (?P<secret>[^"'\s#]{6,})
            ["']?
            """
        ),
    },
    {
        "name": "API Key",
        "severity": "HIGH",
        "variable_pattern": (
            API_KEY_VARIABLE_PATTERN
        ),
        "value_pattern": re.compile(
            r"^[^\s#]{8,}$"
        ),

        # Raw fallback is retained for
        # non-code configuration formats.
        "pattern": re.compile(
            r"""(?ix)
            \b
            (?:
                api[_-]?key
                |
                secret[_-]?key
                |
                client[_-]?secret
                |
                access[_-]?token
                |
                auth[_-]?token
            )
            \b
            \s*[:=]\s*
            ["']?
            (?P<secret>[^"'\s#]{8,})
            ["']?
            """
        ),
    },
]


INLINE_SECRET_PATTERNS = [
    {
        "name": "Bearer Token",
        "severity": "HIGH",
        "pattern": re.compile(
            r"""(?ix)
            \bBearer\s+
            (?P<secret>
                [A-Za-z0-9._\-]{12,}
            )
            """
        ),
    },
    {
        "name": "Database Credential",
        "severity": "CRITICAL",
        "pattern": re.compile(
            r"""(?ix)
            \b
            (?:
                postgres(?:ql)?
                |
                mysql
                |
                mongodb(?:\+srv)?
            )
            ://
            [^:\s]+:
            (?P<secret>[^@\s]+)
            @
            """
        ),
    },
]


# Backward-compatible aggregate for code
# that imports the historical collection.
SECRET_PATTERNS = [
    *ASSIGNMENT_SECRET_PATTERNS,
    *INLINE_SECRET_PATTERNS,
]


def matches_assignment_secret(
    detector: dict,
    variable_name: str,
    value: str,
) -> bool:
    """
    Determine whether a parsed string-literal
    assignment matches a known secret detector.

    This function operates on already parsed
    values rather than arbitrary source-code
    expressions.
    """

    variable_matches = (
        detector[
            "variable_pattern"
        ].fullmatch(
            variable_name
        )
        is not None
    )

    if not variable_matches:
        return False

    return (
        detector[
            "value_pattern"
        ].fullmatch(
            value
        )
        is not None
    )
