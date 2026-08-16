from pathlib import Path

from leakguard.scanner import (
    scan_content,
    scan_path,
)


def test_duplicate_identical_bearer_on_same_line_is_reported_once():
    token = (
        "LEAKGUARDFAKEBEARER12345"
    )

    findings = scan_content(
        path=Path(
            "app.py"
        ),
        content=(
            'message = "Bearer '
            f'{token} Bearer {token}"'
        ),
    )

    bearer_findings = [
        finding
        for finding in findings
        if finding[
            "type"
        ] == "Bearer Token"
    ]

    assert len(
        bearer_findings
    ) == 1

    assert token not in str(
        findings
    )


def test_distinct_bearer_tokens_on_same_line_are_preserved():
    first_token = (
        "LEAKGUARDFAKEBEARER11111"
    )

    second_token = (
        "LEAKGUARDFAKEBEARER22222"
    )

    findings = scan_content(
        path=Path(
            "app.py"
        ),
        content=(
            'message = "Bearer '
            f'{first_token} '
            "Bearer "
            f'{second_token}"'
        ),
    )

    bearer_findings = [
        finding
        for finding in findings
        if finding[
            "type"
        ] == "Bearer Token"
    ]

    assert len(
        bearer_findings
    ) == 2

    assert first_token not in str(
        findings
    )

    assert second_token not in str(
        findings
    )


def test_different_security_signals_on_same_line_are_preserved():
    database_password = (
        "fake_database_password"
    )

    findings = scan_content(
        path=Path(
            "config.py"
        ),
        content=(
            'password = '
            '"postgresql://user:'
            f'{database_password}'
            '@localhost/db"'
        ),
    )

    finding_types = {
        finding[
            "type"
        ]
        for finding in findings
    }

    assert finding_types == {
        "Hardcoded Password",
        "Database Credential",
    }

    assert database_password not in str(
        findings
    )


def test_scan_path_orders_files_deterministically(
    tmp_path,
    monkeypatch,
):
    first_file = (
        tmp_path
        / "a.py"
    )

    second_file = (
        tmp_path
        / "z.py"
    )

    first_file.write_text(
        (
            'password = '
            '"LEAKGUARD_FAKE_PASSWORD_AAA"'
        ),
        encoding="utf-8",
    )

    second_file.write_text(
        (
            'password = '
            '"LEAKGUARD_FAKE_PASSWORD_ZZZ"'
        ),
        encoding="utf-8",
    )

    original_rglob = (
        Path.rglob
    )

    resolved_root = (
        tmp_path.resolve()
    )

    def reversed_rglob(
        self,
        pattern,
    ):
        if (
            self == resolved_root
            and pattern == "*"
        ):
            return iter(
                [
                    second_file,
                    first_file,
                ]
            )

        return original_rglob(
            self,
            pattern,
        )

    monkeypatch.setattr(
        Path,
        "rglob",
        reversed_rglob,
    )

    files_scanned, findings = (
        scan_path(
            tmp_path
        )
    )

    assert files_scanned == 2
    assert len(findings) == 2

    finding_names = [
        Path(
            finding[
                "file"
            ]
        ).name
        for finding in findings
    ]

    assert finding_names == [
        "a.py",
        "z.py",
    ]


def test_repeated_content_scan_returns_identical_findings():
    content = (
        'password = '
        '"LEAKGUARD_FAKE_PASSWORD_123"\n'
        'message = '
        '"Bearer LEAKGUARDFAKEBEARER12345"'
    )

    first = scan_content(
        path=Path(
            "config.py"
        ),
        content=content,
    )

    second = scan_content(
        path=Path(
            "config.py"
        ),
        content=content,
    )

    assert first == second


def test_staged_scan_orders_files_deterministically(
    tmp_path,
    monkeypatch,
):
    from leakguard.staged import (
        scan_staged_path,
    )

    (
        tmp_path
        / ".git"
    ).mkdir()

    first_secret = (
        "LEAKGUARD_FAKE_PASSWORD_AAA"
    )

    second_secret = (
        "LEAKGUARD_FAKE_PASSWORD_ZZZ"
    )

    contents = {
        "a.py": (
            f'password = "{first_secret}"'
            .encode(
                "utf-8"
            )
        ),
        "z.py": (
            f'password = "{second_secret}"'
            .encode(
                "utf-8"
            )
        ),
    }

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_files",
        lambda root: [
            Path(
                "z.py"
            ),
            Path(
                "a.py"
            ),
        ],
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_index_modes",
        lambda root: {
            "a.py": "100644",
            "z.py": "100644",
        },
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "get_staged_file_size",
        lambda root, relative_path: (
            len(
                contents[
                    relative_path.as_posix()
                ]
            )
        ),
    )

    monkeypatch.setattr(
        "leakguard.staged."
        "read_staged_file_bytes",
        lambda root, relative_path: (
            contents[
                relative_path.as_posix()
            ]
        ),
    )

    files_scanned, findings = (
        scan_staged_path(
            tmp_path
        )
    )

    assert files_scanned == 2
    assert len(findings) == 2

    finding_names = [
        Path(
            finding[
                "file"
            ]
        ).name
        for finding in findings
    ]

    assert finding_names == [
        "a.py",
        "z.py",
    ]

    assert first_secret not in str(
        findings
    )

    assert second_secret not in str(
        findings
    )
