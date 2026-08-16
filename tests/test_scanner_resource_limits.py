from leakguard.scan_safety import (
    MAX_SCANNABLE_FILE_BYTES,
)
from leakguard.scanner import (
    scan_path,
)


def test_oversized_supported_file_fails_closed(
    tmp_path,
):
    test_file = (
        tmp_path
        / "large.py"
    )

    with test_file.open(
        "wb"
    ) as handle:
        handle.seek(
            MAX_SCANNABLE_FILE_BYTES
        )

        handle.write(
            b"x"
        )

    files_scanned, findings = (
        scan_path(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert len(findings) == 1

    finding = findings[0]

    assert finding[
        "type"
    ] == (
        "Scan Coverage Limitation"
    )

    assert finding[
        "severity"
    ] == "MEDIUM"

    assert (
        "safe source scan limit"
        in finding[
            "reasons"
        ][0]
    )


def test_binary_supported_file_fails_closed(
    tmp_path,
):
    test_file = (
        tmp_path
        / "binary.py"
    )

    test_file.write_bytes(
        b"print('hello')\x00binary"
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
        "Binary content"
        in findings[
            0
        ][
            "reasons"
        ][0]
    )


def test_normal_text_file_still_scans(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_PASSWORD_123"
    )

    test_file = (
        tmp_path
        / "config.py"
    )

    test_file.write_text(
        f'password = "{secret}"',
        encoding="utf-8",
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
    ] == "Hardcoded Password"

    assert secret not in str(
        findings
    )
