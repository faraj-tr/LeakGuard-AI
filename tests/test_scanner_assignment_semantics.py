from leakguard.scanner import (
    scan_path,
)


def scan_single_file(
    tmp_path,
    filename,
    content,
):
    test_file = (
        tmp_path
        / filename
    )

    test_file.write_text(
        content,
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_path(
            tmp_path
        )
    )

    assert files_scanned == 1

    return findings


def test_password_function_call_is_not_hardcoded_secret(
    tmp_path,
):
    findings = scan_single_file(
        tmp_path,
        "config.py",
        "password = generate_password()",
    )

    assert findings == []


def test_password_getenv_is_not_hardcoded_secret(
    tmp_path,
):
    findings = scan_single_file(
        tmp_path,
        "config.py",
        'password = os.getenv("PASSWORD")',
    )

    assert findings == []


def test_api_key_function_call_is_not_hardcoded_secret(
    tmp_path,
):
    findings = scan_single_file(
        tmp_path,
        "config.py",
        "api_key = load_key()",
    )

    assert findings == []


def test_auth_token_lookup_is_not_hardcoded_secret(
    tmp_path,
):
    findings = scan_single_file(
        tmp_path,
        "config.py",
        'auth_token = config["token"]',
    )

    assert findings == []


def test_hardcoded_password_literal_remains_detected(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_PASSWORD_123"
    )

    findings = scan_single_file(
        tmp_path,
        "config.py",
        f'password = "{secret}"',
    )

    assert len(
        findings
    ) == 1

    assert findings[
        0
    ][
        "type"
    ] == "Hardcoded Password"

    assert secret not in str(
        findings
    )


def test_hardcoded_api_key_literal_remains_detected(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_KEY_ABC123"
    )

    findings = scan_single_file(
        tmp_path,
        "settings.js",
        f'const api_key = "{secret}";',
    )

    assert len(
        findings
    ) == 1

    assert findings[
        0
    ][
        "type"
    ] == "API Key"

    assert secret not in str(
        findings
    )


def test_typed_python_password_literal_is_detected(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_PASSWORD_123"
    )

    findings = scan_single_file(
        tmp_path,
        "config.py",
        f'password: str = "{secret}"',
    )

    assert len(
        findings
    ) == 1

    assert findings[
        0
    ][
        "type"
    ] == "Hardcoded Password"


def test_typed_typescript_api_key_literal_is_detected(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_KEY_ABC123"
    )

    findings = scan_single_file(
        tmp_path,
        "settings.ts",
        (
            "const api_key: string = "
            f'"{secret}";'
        ),
    )

    assert len(
        findings
    ) == 1

    assert findings[
        0
    ][
        "type"
    ] == "API Key"


def test_dotted_password_literal_is_detected(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_PASSWORD_123"
    )

    findings = scan_single_file(
        tmp_path,
        "config.py",
        f'self.password = "{secret}"',
    )

    assert len(
        findings
    ) == 1

    assert findings[
        0
    ][
        "type"
    ] == "Hardcoded Password"


def test_dotenv_unquoted_password_detection_is_preserved(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_PASSWORD_123"
    )

    findings = scan_single_file(
        tmp_path,
        ".env",
        f"DB_PASSWORD={secret}",
    )

    assert len(
        findings
    ) == 1

    assert findings[
        0
    ][
        "type"
    ] == "Hardcoded Password"

    assert secret not in str(
        findings
    )


def test_inline_bearer_and_database_detectors_are_preserved(
    tmp_path,
):
    bearer = (
        "LEAKGUARDFAKEBEARER12345"
    )

    database_password = (
        "fake_database_password"
    )

    test_file = (
        tmp_path
        / "config.py"
    )

    test_file.write_text(
        (
            "header = "
            f'"Bearer {bearer}"\n'
            "database_url = "
            '"postgresql://user:'
            f'{database_password}'
            '@localhost/db"'
        ),
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_path(
            tmp_path
        )
    )

    assert files_scanned == 1

    assert len(
        findings
    ) == 2

    finding_types = {
        finding[
            "type"
        ]
        for finding in findings
    }

    assert finding_types == {
        "Bearer Token",
        "Database Credential",
    }

    assert bearer not in str(
        findings
    )

    assert database_password not in str(
        findings
    )
