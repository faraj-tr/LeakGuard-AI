from leakguard.ignore import (
    get_project_relative_path,
    is_ignored,
    load_ignore_patterns,
)
from leakguard.scanner import (
    scan_path,
    should_skip,
)


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
        (
            'DB_PASSWORD = '
            '"LEAKGUARD_FAKE_PASSWORD_123"'
        ),
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
        (
            'DB_PASSWORD = '
            '"LEAKGUARD_FAKE_PASSWORD_123"'
        ),
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
        scan_path(
            tmp_path
        )
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
        scan_path(
            demo_directory
        )
    )

    assert files_scanned == 1
    assert len(findings) == 1

    assert findings[
        0
    ][
        "type"
    ] == "Hardcoded Password"

    assert secret not in str(
        findings
    )


def test_ignore_file_accepts_utf8_bom(
    tmp_path,
):
    ignore_file = (
        tmp_path
        / ".leakguardignore"
    )

    ignore_file.write_bytes(
        (
            b"\xef\xbb\xbf"
            b"fixtures/\n"
            b"*.log\n"
        )
    )

    patterns = load_ignore_patterns(
        tmp_path
    )

    assert patterns == [
        "fixtures/",
        "*.log",
    ]


def test_ignore_patterns_normalize_windows_separators(
    tmp_path,
):
    ignore_file = (
        tmp_path
        / ".leakguardignore"
    )

    ignore_file.write_text(
        (
            "fixtures\\generated\\\n"
        ),
        encoding="utf-8",
    )

    patterns = load_ignore_patterns(
        tmp_path
    )

    assert patterns == [
        "fixtures/generated/"
    ]


def test_project_relative_path_normalizes_dotdot_without_symlink_resolution(
    tmp_path,
):
    root = (
        tmp_path
        / "project"
    )

    root.mkdir()

    candidate = (
        root
        / "nested"
        / ".."
        / "config.py"
    )

    relative = (
        get_project_relative_path(
            path=candidate,
            root=root,
        )
    )

    assert relative is not None

    assert (
        relative.as_posix()
        == "config.py"
    )


def test_project_relative_path_rejects_outside_root(
    tmp_path,
):
    root = (
        tmp_path
        / "project"
    )

    root.mkdir()

    outside = (
        tmp_path
        / "outside.py"
    )

    assert (
        get_project_relative_path(
            path=outside,
            root=root,
        )
        is None
    )


def test_should_skip_path_outside_root(
    tmp_path,
):
    root = (
        tmp_path
        / "project"
    )

    root.mkdir()

    outside = (
        tmp_path
        / "outside.py"
    )

    assert should_skip(
        path=outside,
        root=root,
        ignore_patterns=[],
    ) is True


def test_scan_root_does_not_inherit_parent_skip_directory_name(
    tmp_path,
):
    parent = (
        tmp_path
        / ".venv"
    )

    root = (
        parent
        / "actual_project"
    )

    root.mkdir(
        parents=True
    )

    secret = (
        "LEAKGUARD_FAKE_PASSWORD_123"
    )

    test_file = (
        root
        / "config.py"
    )

    test_file.write_text(
        f'password = "{secret}"',
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_path(
            root
        )
    )

    assert files_scanned == 1
    assert len(findings) == 1

    assert findings[
        0
    ][
        "type"
    ] == "Hardcoded Password"

    assert secret not in str(
        findings
    )
