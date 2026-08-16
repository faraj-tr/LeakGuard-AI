from leakguard.scan_safety import (
    MAX_SCANNABLE_FILE_BYTES,
    build_scan_limitation_finding,
    evaluate_content_bytes,
    evaluate_file_size,
    is_probably_binary,
)


def test_normal_file_size_is_allowed():
    result = evaluate_file_size(
        1024
    )

    assert result.safe_to_scan is True
    assert result.reason is None


def test_oversized_file_is_rejected():
    result = evaluate_file_size(
        MAX_SCANNABLE_FILE_BYTES
        + 1
    )

    assert result.safe_to_scan is False

    assert (
        "exceeds"
        in result.reason
    )


def test_null_byte_is_binary_evidence():
    assert is_probably_binary(
        b"print('hello')\x00data"
    ) is True


def test_normal_source_is_not_binary():
    assert is_probably_binary(
        b'password = "fake-value"\n'
    ) is False


def test_content_size_has_defense_in_depth():
    content = (
        b"a"
        * (
            MAX_SCANNABLE_FILE_BYTES
            + 1
        )
    )

    result = evaluate_content_bytes(
        content
    )

    assert result.safe_to_scan is False


def test_scan_limitation_does_not_contain_secret_data():
    finding = (
        build_scan_limitation_finding(
            path=__file__,
            reason=(
                "Binary content detected."
            ),
        )
    )

    assert finding[
        "type"
    ] == (
        "Scan Coverage Limitation"
    )

    assert finding[
        "severity"
    ] == "MEDIUM"

    assert finding[
        "masked_value"
    ] == "-"
