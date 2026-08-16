from pathlib import Path

from leakguard.scanner import (
    scan_content,
    scan_path,
)


TEST_SECRET = (
    "K7mP2xQ9vL4sN8zA1c"
)


def test_scan_content_accepts_utf8_bom_before_first_assignment():
    content = (
        "\ufeff"
        f'x = "{TEST_SECRET}"'
    )

    findings = scan_content(
        path=Path(
            "mystery.py"
        ),
        content=content,
    )

    assert len(
        findings
    ) == 1

    finding = findings[0]

    assert finding[
        "line"
    ] == 1

    assert finding[
        "type"
    ] == (
        "Unknown Secret Candidate"
    )

    assert TEST_SECRET not in str(
        findings
    )


def test_scan_path_detects_secret_in_utf8_bom_file(
    tmp_path,
):
    test_file = (
        tmp_path
        / "mystery.py"
    )

    test_file.write_bytes(
        (
            b"\xef\xbb\xbf"
            + (
                f'x = "{TEST_SECRET}"'
            ).encode(
                "utf-8"
            )
        )
    )

    files_scanned, findings = (
        scan_path(
            tmp_path
        )
    )

    assert files_scanned == 1

    assert len(
        findings
    ) == 1

    assert findings[
        0
    ][
        "line"
    ] == 1

    assert TEST_SECRET not in str(
        findings
    )
