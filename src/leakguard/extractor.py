import re


CODE_LITERAL_ASSIGNMENT_PATTERN = re.compile(
    r"""
    ^\s*

    # Optional JavaScript / TypeScript declaration.
    (?:
        (?:export\s+)?
        (?:const|let|var)
        \s+
    )?

    # Simple or dotted assignment target.
    (?P<target>
        [A-Za-z_$][A-Za-z0-9_$]*
        (?:
            \.
            [A-Za-z_$][A-Za-z0-9_$]*
        )*
    )

    # Optional Python / TypeScript type annotation.
    (?:
        \s*:\s*
        [^=]+?
    )?

    # Real assignment operator, not ==.
    \s*=(?!=)\s*

    # Optional Python literal prefix.
    (?:
        [rRuUbB]{1,2}
    )?

    # Supported quoted string literal.
    (?:
        "
        (?P<double_value>
            (?:\\.|[^"\\])*
        )
        "
        |
        '
        (?P<single_value>
            (?:\\.|[^'\\])*
        )
        '
    )

    # Optional JavaScript semicolon.
    \s*;?

    # Optional trailing comment.
    \s*
    (?:
        (?:\#|//).*
    )?

    \s*$
    """,
    re.VERBOSE,
)


PROPERTY_LITERAL_ASSIGNMENT_PATTERN = re.compile(
    r"""
    ^\s*

    # JSON / YAML / object-style property.
    (?:
        "
        (?P<double_variable>
            [A-Za-z_][A-Za-z0-9_-]*
        )
        "
        |
        '
        (?P<single_variable>
            [A-Za-z_][A-Za-z0-9_-]*
        )
        '
        |
        (?P<bare_variable>
            [A-Za-z_][A-Za-z0-9_-]*
        )
    )

    \s*:\s*

    # Quoted literal value.
    (?:
        "
        (?P<property_double_value>
            (?:\\.|[^"\\])*
        )
        "
        |
        '
        (?P<property_single_value>
            (?:\\.|[^'\\])*
        )
        '
    )

    \s*,?

    # Optional YAML / JavaScript comment.
    \s*
    (?:
        (?:\#|//).*
    )?

    \s*$
    """,
    re.VERBOSE,
)


CODE_EXPRESSION_ASSIGNMENT_PATTERN = re.compile(
    r"""
    ^\s*

    # Optional JavaScript / TypeScript declaration.
    (?:
        (?:export\s+)?
        (?:const|let|var)
        \s+
    )?

    # Simple or dotted assignment target.
    (?P<target>
        [A-Za-z_$][A-Za-z0-9_$]*
        (?:
            \.
            [A-Za-z_$][A-Za-z0-9_$]*
        )*
    )

    # Optional Python / TypeScript type annotation.
    (?:
        \s*:\s*
        [^=]+?
    )?

    # Real assignment operator, not ==.
    \s*=(?!=)\s*

    # Any non-empty unsupported right-hand side.
    (?P<expression>
        .+?
    )

    \s*;?
    \s*$
    """,
    re.VERBOSE,
)


def _final_target_name(
    target: str,
) -> str:
    """
    Return the final identifier from a
    dotted assignment target.

    Example:
        self.password -> password
        config.api_key -> api_key
    """

    return target.rsplit(
        ".",
        maxsplit=1,
    )[-1]


def _extract_code_literal(
    line: str,
) -> dict | None:
    match = (
        CODE_LITERAL_ASSIGNMENT_PATTERN
        .match(
            line
        )
    )

    if match is None:
        return None

    value = match.group(
        "double_value"
    )

    if value is None:
        value = match.group(
            "single_value"
        )

    return {
        "variable_name": (
            _final_target_name(
                match.group(
                    "target"
                )
            )
        ),
        "value": value,
    }


def _extract_property_literal(
    line: str,
) -> dict | None:
    match = (
        PROPERTY_LITERAL_ASSIGNMENT_PATTERN
        .match(
            line
        )
    )

    if match is None:
        return None

    variable_name = (
        match.group(
            "double_variable"
        )
        or match.group(
            "single_variable"
        )
        or match.group(
            "bare_variable"
        )
    )

    value = match.group(
        "property_double_value"
    )

    if value is None:
        value = match.group(
            "property_single_value"
        )

    return {
        "variable_name": variable_name,
        "value": value,
    }


def extract_assignment(
    line: str,
) -> dict | None:
    """
    Extract a supported string-literal
    assignment.

    Expressions and unsupported right-hand
    sides intentionally return None.
    """

    code_assignment = (
        _extract_code_literal(
            line
        )
    )

    if code_assignment is not None:
        return code_assignment

    return _extract_property_literal(
        line
    )


def classify_assignment(
    line: str,
) -> dict | None:
    """
    Classify a supported assignment.

    "literal" means LeakGuard extracted a
    concrete string value that exists in
    source code.

    "expression" means an assignment exists,
    but its right-hand side is not a supported
    fixed string literal.

    This classification is intentionally
    conservative and is not a complete
    programming-language parser.
    """

    literal = extract_assignment(
        line
    )

    if literal is not None:
        return {
            "kind": "literal",
            "variable_name": literal[
                "variable_name"
            ],
            "value": literal[
                "value"
            ],
        }

    expression_match = (
        CODE_EXPRESSION_ASSIGNMENT_PATTERN
        .match(
            line
        )
    )

    if expression_match is None:
        return None

    return {
        "kind": "expression",
        "variable_name": (
            _final_target_name(
                expression_match.group(
                    "target"
                )
            )
        ),
        "value": None,
    }
