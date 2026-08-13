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

    # Raw secrets must never appear in scanner results.
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


def test_scanner_detects_unknown_random_candidate(tmp_path):
    secret = "K7mP2xQ9vL4sN8zA1c"

    test_file = tmp_path / "mystery.py"

    test_file.write_text(
        f'x = "{secret}"',
        encoding="utf-8",
    )

    files_scanned, findings = scan_path(tmp_path)

    assert files_scanned == 1
    assert len(findings) == 1

    finding = findings[0]

    assert finding["type"] == "Unknown Secret Candidate"
    assert finding["severity"] == "MEDIUM"
    assert finding["candidate_score"] >= 50

    # Raw suspicious values must never be exposed.
    assert secret not in str(findings)
def test_scanner_detects_vite_client_secret_exposure(tmp_path):
    secret = "LEAKGUARD_FAKE_KEY_ABC123"

    env_file = tmp_path / ".env"

    env_file.write_text(
        f"VITE_OPENAI_API_KEY={secret}",
        encoding="utf-8",
    )

    files_scanned, findings = scan_path(
        tmp_path
    )

    assert files_scanned == 1
    assert len(findings) == 1

    finding = findings[0]

    assert finding["type"] == (
        "Client-Side Secret Exposure"
    )

    assert finding["severity"] == "CRITICAL"
    assert finding["framework"] == "Vite"

    assert secret not in str(findings)


def test_scanner_ignores_public_vite_ui_variable(tmp_path):
    env_file = tmp_path / ".env"

    env_file.write_text(
        "VITE_APP_TITLE=LeakGuard",
        encoding="utf-8",
    )

    files_scanned, findings = scan_path(
        tmp_path
    )

    assert files_scanned == 1
    assert findings == []