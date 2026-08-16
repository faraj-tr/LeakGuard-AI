from pathlib import Path

from leakguard.scanner import (
    scan_file,
    scan_path,
)


def test_scan_file_refuses_symbolic_link_semantics(
    tmp_path,
    monkeypatch,
):
    test_file = (
        tmp_path
        / "link.py"
    )

    test_file.write_text(
        'message = "safe"',
        encoding="utf-8",
    )

    original_is_symlink = (
        Path.is_symlink
    )

    def fake_is_symlink(
        self,
    ):
        if self == test_file:
            return True

        return original_is_symlink(
            self
        )

    monkeypatch.setattr(
        Path,
        "is_symlink",
        fake_is_symlink,
    )

    findings = scan_file(
        test_file
    )

    assert len(findings) == 1

    assert findings[
        0
    ][
        "type"
    ] == (
        "Scan Coverage Limitation"
    )

    assert (
        "Symbolic links"
        in findings[
            0
        ][
            "reasons"
        ][0]
    )


def test_scan_file_stat_failure_fails_closed(
    tmp_path,
    monkeypatch,
):
    test_file = (
        tmp_path
        / "config.py"
    )

    test_file.write_text(
        'message = "safe"',
        encoding="utf-8",
    )

    original_stat = Path.stat

    def fake_stat(
        self,
        *args,
        **kwargs,
    ):
        if self == test_file:
            raise OSError(
                "simulated metadata failure"
            )

        return original_stat(
            self,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        Path,
        "stat",
        fake_stat,
    )

    findings = scan_file(
        test_file
    )

    assert len(findings) == 1

    assert findings[
        0
    ][
        "type"
    ] == (
        "Scan Coverage Limitation"
    )

    assert (
        "metadata"
        in findings[
            0
        ][
            "reasons"
        ][0]
    )


def test_scan_file_read_failure_fails_closed(
    tmp_path,
    monkeypatch,
):
    test_file = (
        tmp_path
        / "config.py"
    )

    test_file.write_text(
        'message = "safe"',
        encoding="utf-8",
    )

    original_read_bytes = (
        Path.read_bytes
    )

    def fake_read_bytes(
        self,
    ):
        if self == test_file:
            raise OSError(
                "simulated read failure"
            )

        return original_read_bytes(
            self
        )

    monkeypatch.setattr(
        Path,
        "read_bytes",
        fake_read_bytes,
    )

    findings = scan_file(
        test_file
    )

    assert len(findings) == 1

    assert findings[
        0
    ][
        "type"
    ] == (
        "Scan Coverage Limitation"
    )

    assert (
        "content"
        in findings[
            0
        ][
            "reasons"
        ][0]
    )


def test_scan_path_handles_supported_symlink_as_coverage_limitation(
    tmp_path,
    monkeypatch,
):
    test_file = (
        tmp_path
        / "link.py"
    )

    test_file.write_text(
        'message = "safe"',
        encoding="utf-8",
    )

    original_is_symlink = (
        Path.is_symlink
    )

    def fake_is_symlink(
        self,
    ):
        if self == test_file:
            return True

        return original_is_symlink(
            self
        )

    monkeypatch.setattr(
        Path,
        "is_symlink",
        fake_is_symlink,
    )

    files_scanned, findings = (
        scan_path(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert len(findings) == 1

    assert findings[
        0
    ][
        "type"
    ] == (
        "Scan Coverage Limitation"
    )


def test_scan_path_metadata_inspection_failure_fails_closed(
    tmp_path,
    monkeypatch,
):
    test_file = (
        tmp_path
        / "config.py"
    )

    test_file.write_text(
        'message = "safe"',
        encoding="utf-8",
    )

    original_is_symlink = (
        Path.is_symlink
    )

    def fake_is_symlink(
        self,
    ):
        if self == test_file:
            raise OSError(
                "simulated traversal "
                "metadata failure"
            )

        return original_is_symlink(
            self
        )

    monkeypatch.setattr(
        Path,
        "is_symlink",
        fake_is_symlink,
    )

    files_scanned, findings = (
        scan_path(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert len(findings) == 1

    assert findings[
        0
    ][
        "type"
    ] == (
        "Scan Coverage Limitation"
    )

    assert (
        "metadata"
        in findings[
            0
        ][
            "reasons"
        ][0].lower()
    )
