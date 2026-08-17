import subprocess

from fastapi.testclient import (
    TestClient,
)

from leakguard.api.app import (
    create_app,
)


def build_client(
    root,
    *,
    raise_server_exceptions=True,
):
    return TestClient(
        create_app(
            scan_root=root
        ),
        raise_server_exceptions=(
            raise_server_exceptions
        ),
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

    client = build_client(
        tmp_path
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": ".",
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

    client = build_client(
        tmp_path
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": ".",
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

    client = build_client(
        tmp_path
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": ".",
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

    config_file.write_text(
        'message = "safe"',
        encoding="utf-8",
    )

    client = build_client(
        tmp_path
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": ".",
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
    client = build_client(
        tmp_path
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": "does-not-exist",
            "ml_advisory": False,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "error": {
            "code": "project_not_found",
            "message": (
                "Project path does not exist."
            ),
        }
    }


def test_api_rejects_unknown_security_controls(
    tmp_path,
):
    rejected_value = (
        "LEAKGUARD_FAKE_REJECTED_VALUE_123"
    )

    client = build_client(
        tmp_path
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": ".",
            "ml_advisory": False,
            "blocking": rejected_value,
        },
    )

    assert response.status_code == 422

    assert response.json() == {
        "error": {
            "code": "invalid_request",
            "message": (
                "Request validation failed."
            ),
        }
    }

    assert rejected_value not in (
        response.text
    )


def test_api_resolves_relative_path_inside_root(
    tmp_path,
):
    project = (
        tmp_path
        / "project"
    )

    project.mkdir()

    (
        project
        / "app.py"
    ).write_text(
        'message = "safe"',
        encoding="utf-8",
    )

    client = build_client(
        tmp_path
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": "project",
            "ml_advisory": False,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["files_scanned"] == 1
    assert payload["gate"] == "passed"


def test_api_rejects_absolute_path_outside_root(
    tmp_path,
):
    allowed = (
        tmp_path
        / "allowed"
    )

    outside = (
        tmp_path
        / "outside"
    )

    allowed.mkdir()
    outside.mkdir()

    client = build_client(
        allowed
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": str(
                outside
            ),
            "ml_advisory": False,
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "error": {
            "code": (
                "path_outside_scan_root"
            ),
            "message": (
                "Requested project is outside "
                "the configured API scan root."
            ),
        }
    }

    assert str(
        outside
    ) not in response.text


def test_api_rejects_parent_traversal(
    tmp_path,
):
    allowed = (
        tmp_path
        / "allowed"
    )

    outside = (
        tmp_path
        / "outside"
    )

    allowed.mkdir()
    outside.mkdir()

    client = build_client(
        allowed
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": "../outside",
            "ml_advisory": False,
        },
    )

    assert response.status_code == 403

    assert (
        response.json()[
            "error"
        ][
            "code"
        ]
        == "path_outside_scan_root"
    )


def test_api_malformed_json_is_not_reflected(
    tmp_path,
):
    rejected_value = (
        "LEAKGUARD_FAKE_MALFORMED_SECRET_123"
    )

    client = build_client(
        tmp_path
    )

    response = client.post(
        "/v1/scan",
        content=(
            '{"path": ".", '
            f'"value": "{rejected_value}"'
        ),
        headers={
            "content-type": (
                "application/json"
            )
        },
    )

    assert response.status_code == 422

    assert response.json() == {
        "error": {
            "code": "invalid_request",
            "message": (
                "Request validation failed."
            ),
        }
    }

    assert rejected_value not in (
        response.text
    )


def test_openapi_exposes_no_ml_blocking_authority(
    tmp_path,
):
    client = build_client(
        tmp_path
    )

    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    schema = response.json()

    request_schema = (
        schema[
            "components"
        ][
            "schemas"
        ][
            "ScanRequest"
        ]
    )

    properties = (
        request_schema[
            "properties"
        ]
    )

    assert set(
        properties
    ) == {
        "path",
        "staged",
        "ml_advisory",
    }

    assert "blocking" not in (
        properties
    )

    assert (
        request_schema[
            "additionalProperties"
        ]
        is False
    )


def test_api_internal_error_is_generic(
    tmp_path,
    monkeypatch,
):
    internal_secret = (
        "LEAKGUARD_INTERNAL_SECRET_ABC123"
    )

    def explode(
        *args,
        **kwargs,
    ):
        raise RuntimeError(
            internal_secret
        )

    monkeypatch.setattr(
        "leakguard.api.app."
        "run_security_scan",
        explode,
    )

    client = build_client(
        tmp_path,
        raise_server_exceptions=False,
    )

    response = client.post(
        "/v1/scan",
        json={
            "path": ".",
            "ml_advisory": False,
        },
    )

    assert response.status_code == 500

    assert response.json() == {
        "error": {
            "code": "internal_error",
            "message": (
                "Internal server error."
            ),
        }
    }

    assert internal_secret not in (
        response.text
    )
