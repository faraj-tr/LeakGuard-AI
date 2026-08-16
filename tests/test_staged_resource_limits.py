from pathlib import Path

from leakguard.scan_safety import (
    MAX_SCANNABLE_FILE_BYTES,
)
from leakguard.staged import (
    scan_staged_path,
)


def prepare_fake_git_root(
    tmp_path,
):
    git_directory = (
        tmp_path
        / ".git"
    )

    git_directory.mkdir()

    return tmp_path


def install_regular_mode(
    monkeypatch,
    path_name,
):
    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_index_modes",
        lambda root: {
            path_name: "100644"
        },
    )


def test_oversized_staged_blob_is_not_read(
    tmp_path,
    monkeypatch,
):
    root = prepare_fake_git_root(
        tmp_path
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_files",
        lambda root: [
            Path(
                "large.py"
            )
        ],
    )

    install_regular_mode(
        monkeypatch,
        "large.py",
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_file_size",
        lambda root, relative_path: (
            MAX_SCANNABLE_FILE_BYTES
            + 1
        ),
    )

    def forbidden_read(
        root,
        relative_path,
    ):
        raise AssertionError(
            "Oversized staged blob "
            "must not be loaded."
        )

    monkeypatch.setattr(
        "leakguard.staged."
        "read_staged_file_bytes",
        forbidden_read,
    )

    files_scanned, findings = (
        scan_staged_path(
            root
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


def test_binary_staged_blob_fails_closed(
    tmp_path,
    monkeypatch,
):
    root = prepare_fake_git_root(
        tmp_path
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_files",
        lambda root: [
            Path(
                "binary.py"
            )
        ],
    )

    install_regular_mode(
        monkeypatch,
        "binary.py",
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_file_size",
        lambda root, relative_path: 24,
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "read_staged_file_bytes",
        lambda root, relative_path: (
            b"print('hello')\x00binary"
        ),
    )

    files_scanned, findings = (
        scan_staged_path(
            root
        )
    )

    assert files_scanned == 1
    assert len(findings) == 1

    assert (
        "Binary content"
        in findings[
            0
        ][
            "reasons"
        ][0]
    )


def test_normal_staged_blob_still_scans(
    tmp_path,
    monkeypatch,
):
    root = prepare_fake_git_root(
        tmp_path
    )

    secret = (
        "LEAKGUARD_FAKE_PASSWORD_123"
    )

    content = (
        f'password = "{secret}"'
        .encode(
            "utf-8"
        )
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_files",
        lambda root: [
            Path(
                "config.py"
            )
        ],
    )

    install_regular_mode(
        monkeypatch,
        "config.py",
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_file_size",
        lambda root, relative_path: (
            len(
                content
            )
        ),
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "read_staged_file_bytes",
        lambda root, relative_path: (
            content
        ),
    )

    files_scanned, findings = (
        scan_staged_path(
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
