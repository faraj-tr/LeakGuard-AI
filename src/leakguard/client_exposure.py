from leakguard.candidate import (
    analyze_candidate,
    has_sensitive_name,
)


CLIENT_EXPOSED_PREFIXES = {
    "VITE_": "Vite",
    "NEXT_PUBLIC_": "Next.js",
}


def detect_client_framework(
    variable_name: str,
) -> str | None:
    """
    Detect whether an environment variable uses
    a known client-exposed framework prefix.
    """

    upper_name = variable_name.upper()

    for prefix, framework in CLIENT_EXPOSED_PREFIXES.items():

        if upper_name.startswith(prefix):
            return framework

    return None


def remove_client_prefix(
    variable_name: str,
) -> str:
    """
    Remove a known frontend environment prefix
    before analyzing the semantic variable name.
    """

    upper_name = variable_name.upper()

    for prefix in CLIENT_EXPOSED_PREFIXES:

        if upper_name.startswith(prefix):
            return variable_name[len(prefix):]

    return variable_name


def analyze_client_exposure(
    variable_name: str,
    value: str,
) -> dict:
    """
    Analyze whether an environment variable may expose
    a secret to client-side application code.

    Client exposure and secret detection are separate
    signals. A public variable is not automatically
    considered a secret.
    """

    framework = detect_client_framework(
        variable_name
    )

    if framework is None:
        return {
            "is_client_exposed": False,
            "is_risky": False,
            "framework": None,
            "severity": None,
            "candidate_score": 0,
            "reasons": [],
        }

    semantic_name = remove_client_prefix(
        variable_name
    )

    candidate = analyze_candidate(
        variable_name=semantic_name,
        value=value,
    )

    sensitive_name = has_sensitive_name(
        semantic_name
    )

    is_risky = (
        sensitive_name
        or candidate["is_suspicious"]
    )

    reasons = [
        "Client-exposed environment variable"
    ]

    if sensitive_name:
        reasons.append(
            "Sensitive credential name"
        )

    for reason in candidate["reasons"]:

        if reason not in reasons:
            reasons.append(reason)

    return {
        "is_client_exposed": True,
        "is_risky": is_risky,
        "framework": framework,
        "severity": (
            "CRITICAL"
            if is_risky
            else None
        ),
        "candidate_score": candidate["score"],
        "reasons": reasons,
    }