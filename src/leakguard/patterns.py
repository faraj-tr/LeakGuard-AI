import re


SECRET_PATTERNS = [
    {
        "name": "Hardcoded Password",
        "severity": "HIGH",
        "pattern": re.compile(
            r"""(?ix)
           \b(?:[A-Za-z0-9]+[_-])*(?:password|passwd|pwd)\b
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
        "pattern": re.compile(
            r"""(?ix)
            \b(?:api[_-]?key|secret[_-]?key|client[_-]?secret|
                access[_-]?token|auth[_-]?token)\b
            \s*[:=]\s*
            ["']?
            (?P<secret>[^"'\s#]{8,})
            ["']?
            """
        ),
    },

    {
        "name": "Bearer Token",
        "severity": "HIGH",
        "pattern": re.compile(
            r"""(?ix)
            \bBearer\s+
            (?P<secret>[A-Za-z0-9._\-]{12,})
            """
        ),
    },

    {
        "name": "Database Credential",
        "severity": "CRITICAL",
        "pattern": re.compile(
            r"""(?ix)
            \b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)
            ://
            [^:\s]+:
            (?P<secret>[^@\s]+)
            @
            """
        ),
    },
]