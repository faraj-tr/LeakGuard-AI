from pathlib import Path

import pytest

from leakguard.staged import (
    GitStagedScanError,
    get_staged_index_modes,
    scan_staged_path,
)


def prepare_fake_git_root(
    tmp_path,
):
    (
        tmp_path
        / ".git"
    ).mkdir()

    return tmp_path


def test_parses_git_index_file_modes(
    tmp_path,
    monkeypatch,
):
    output = (
        b"100644 abc123 0\tconfig.py\0"
        b"120000 def456 0\tlink.py\0"
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "run_git_command",
        lambda root, arguments: output,
    )

    modes = get_staged_index_modes(
        tmp_path
    )

    assert modes == {
        "config.py": "100644",
        "link.py": "120000",
    }


def test_malformed_git_index_metadata_is_rejected(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "leakguard.staged."
        "run_git_command",
        lambda root, arguments: (
            b"malformed-record\0"
        ),
    )

    with pytest.raises(
        GitStagedScanError,
        match="malformed",
    ):
        get_staged_index_modes(
            tmp_path
        )


def test_unmerged_git_index_entry_is_rejected(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "leakguard.staged."
        "run_git_command",
        lambda root, arguments: (
            b"100644 abc123 2\tconfig.py\0"
        ),
    )

    with pytest.raises(
        GitStagedScanError,
        match="Unmerged",
    ):
        get_staged_index_modes(
            tmp_path
        )


def test_non_regular_staged_entry_fails_closed_without_reading_blob(
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
                "link.py"
            )
        ],
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_index_modes",
        lambda root: {
            "link.py": "120000"
        },
    )

    def forbidden_size(
        root,
        relative_path,
    ):
        raise AssertionError(
            "Non-regular staged entry "
            "must not be inspected as "
            "a normal blob."
        )

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_file_size",
        forbidden_size,
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

    assert (
        "not a regular file"
        in findings[
            0
        ][
            "reasons"
        ][0]
    )

    assert (
        "120000"
        in findings[
            0
        ][
            "reasons"
        ][0]
    )


def test_missing_staged_git_mode_is_rejected(
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
                "config.py"
            )
        ],
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_index_modes",
        lambda root: {},
    )

    with pytest.raises(
        GitStagedScanError,
        match="Unable to determine",
    ):
        scan_staged_path(
            root
        )
