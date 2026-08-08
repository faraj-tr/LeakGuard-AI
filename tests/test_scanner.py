from leakguard.scanner import scan_path


def test_scanner_detects_prefixed_password_variable(tmp_path):
    secret = "LEAKGUARD_FAKE_PASSWORD_123"

    test_file = tmp_path / "config.py"

    test_file.write_text(
        f'DB_PASSWORD = "{secret}"',
        encoding="utf-8",
    )

    files_scanned, findings = scan_path(tmp_path)

    assert files_scanned == 1
    assert len(findings) == 1

    assert findings[0]["type"] == "Hardcoded Password"

    # The real secret must never appear in scanner results.
    assert secret not in str(findings)


def test_scanner_ignores_password_ui_text(tmp_path):
    test_file = tmp_path / "app.py"

    test_file.write_text(
        'WELCOME_MESSAGE = "Please enter your password"',
        encoding="utf-8",
    )

    files_scanned, findings = scan_path(tmp_path)

    assert files_scanned == 1
    assert findings == []