def mask_secret(value: str) -> str:
    """
    Hide sensitive values before displaying them.

    LeakGuard should never print a complete secret.
    """

    value = value.strip()

    if not value:
        return ""

    if len(value) <= 8:
        return "*" * len(value)

    return f"{value[:4]}********{value[-4:]}"