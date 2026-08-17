import subprocess

from fastapi.testclient import (
    TestClient,
)

from leakguard.api.app import app


client = TestClient(
    app
)


def initialize_git_repository(
    root,
):
    subprocess.run(
        [
            "git",
            "init",
        ],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def stage_file(
    root,
    path,
):
    subprocess.run(
        [
            "git",
            "add",
            path,
        ],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_api_scan_clean_project(
    tmp_path,
):
    (
        tmp_path
        / "app.py"
    ).write_text(
        'message = "Hello world"',
        encoding="utf-8",
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": str(
                tmp_path
            ),
            "ml_advisory": False,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["mode"] == "project"
    assert payload["files_scanned"] == 1
    assert payload["findings_count"] == 0
    assert payload["gate"] == "passed"

    assert (
        payload[
            "ml_advisory_enabled"
        ]
        is False
    )

    assert payload["findings"] == []


def test_api_scan_returns_masked_finding(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_PASSWORD_API_123"
    )

    (
        tmp_path
        / "config.py"
    ).write_text(
        (
            'DB_PASSWORD = '
            f'"{secret}"'
        ),
        encoding="utf-8",
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": str(
                tmp_path
            ),
            "ml_advisory": False,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["gate"] == "failed"
    assert payload["findings_count"] == 1

    assert (
        payload[
            "severity_counts"
        ][
            "high"
        ]
        == 1
    )

    finding = payload[
        "findings"
    ][0]

    assert (
        finding["type"]
        == "Hardcoded Password"
    )

    assert finding["file"] == "config.py"

    assert secret not in (
        response.text
    )


def test_api_scan_includes_artifact_exposure(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_KEY_API_ABC123"
    )

    (
        tmp_path
        / ".env"
    ).write_text(
        f"API_KEY={secret}",
        encoding="utf-8",
    )

    artifact = (
        tmp_path
        / "dist"
        / "app.js"
    )

    artifact.parent.mkdir(
        parents=True,
    )

    artifact.write_text(
        (
            'const config={key:"'
            f'{secret}'
            '"};'
        ),
        encoding="utf-8",
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": str(
                tmp_path
            ),
            "ml_advisory": False,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["files_scanned"] == 2
    assert payload["gate"] == "failed"

    finding_types = {
        finding["type"]
        for finding in payload[
            "findings"
        ]
    }

    assert "API Key" in finding_types

    assert (
        "Artifact Secret Exposure"
        in finding_types
    )

    assert (
        payload[
            "severity_counts"
        ][
            "critical"
        ]
        == 1
    )

    assert secret not in (
        response.text
    )


def test_api_staged_scan_uses_git_index(
    tmp_path,
):
    initialize_git_repository(
        tmp_path
    )

    secret = (
        "LEAKGUARD_FAKE_PASSWORD_STAGE_API_123"
    )

    config_file = (
        tmp_path
        / "config.py"
    )

    config_file.write_text(
        (
            'DB_PASSWORD = '
            f'"{secret}"'
        ),
        encoding="utf-8",
    )

    stage_file(
        tmp_path,
        "config.py",
    )

    # Working-tree content changes after
    # staging. API staged mode must still
    # inspect the staged dangerous version.
    config_file.write_text(
        'message = "safe"',
        encoding="utf-8",
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": str(
                tmp_path
            ),
            "staged": True,
            "ml_advisory": False,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["mode"] == "staged"
    assert payload["files_scanned"] == 1
    assert payload["gate"] == "failed"

    assert (
        payload[
            "findings"
        ][0][
            "type"
        ]
        == "Hardcoded Password"
    )

    assert secret not in (
        response.text
    )


def test_api_scan_missing_path_returns_404(
    tmp_path,
):
    missing = (
        tmp_path
        / "does-not-exist"
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": str(
                missing
            ),
            "ml_advisory": False,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "Project path does not exist."
        )
    }


def test_api_rejects_unknown_security_controls(
    tmp_path,
):
    response = client.post(
        "/v1/scan",
        json={
            "path": str(
                tmp_path
            ),
            "ml_advisory": False,
            "blocking": True,
        },
    )

    assert response.status_code == 422
