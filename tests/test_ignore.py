from leakguard.ignore import (
    is_ignored,
    load_ignore_patterns,
)
from leakguard.scanner import scan_path


def test_loads_leakguard_ignore_patterns(
    tmp_path,
):
    ignore_file = (
        tmp_path
        / ".leakguardignore"
    )

    ignore_file.write_text(
        """
# LeakGuard test rules

demo_project/
*.log
""",
        encoding="utf-8",
    )

    patterns = load_ignore_patterns(
        tmp_path
    )

    assert patterns == [
        "demo_project/",
        "*.log",
    ]


def test_matches_ignored_directory(
    tmp_path,
):
    demo_directory = (
        tmp_path
        / "demo_project"
    )

    demo_directory.mkdir()

    secret_file = (
        demo_directory
        / "config.py"
    )

    secret_file.write_text(
        'DB_PASSWORD = "LEAKGUARD_FAKE_PASSWORD_123"',
        encoding="utf-8",
    )

    patterns = [
        "demo_project/"
    ]

    assert is_ignored(
        path=secret_file,
        root=tmp_path,
        patterns=patterns,
    ) is True


def test_scanner_skips_ignored_directory(
    tmp_path,
):
    demo_directory = (
        tmp_path
        / "demo_project"
    )

    demo_directory.mkdir()

    secret_file = (
        demo_directory
        / "config.py"
    )

    secret_file.write_text(
        'DB_PASSWORD = "LEAKGUARD_FAKE_PASSWORD_123"',
        encoding="utf-8",
    )

    ignore_file = (
        tmp_path
        / ".leakguardignore"
    )

    ignore_file.write_text(
        "demo_project/\n",
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_path(tmp_path)
    )

    assert files_scanned == 0
    assert findings == []


def test_direct_scan_does_not_inherit_parent_ignore(
    tmp_path,
):
    demo_directory = (
        tmp_path
        / "demo_project"
    )

    demo_directory.mkdir()

    secret = (
        "LEAKGUARD_FAKE_PASSWORD_123"
    )

    secret_file = (
        demo_directory
        / "config.py"
    )

    secret_file.write_text(
        f'DB_PASSWORD = "{secret}"',
        encoding="utf-8",
    )

    parent_ignore_file = (
        tmp_path
        / ".leakguardignore"
    )

    parent_ignore_file.write_text(
        "demo_project/\n",
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_path(demo_directory)
    )

    assert files_scanned == 1
    assert len(findings) == 1

    assert findings[0][
        "type"
    ] == "Hardcoded Password"

    assert secret not in str(
        findings
    )