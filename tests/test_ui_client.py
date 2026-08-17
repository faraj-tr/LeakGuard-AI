import pytest

from leakguard.ui.client import (
    LeakGuardApiClient,
    LeakGuardApiResponseError,
)


def test_ui_client_builds_health_url():
    client = LeakGuardApiClient(
        base_url=(
            "http://127.0.0.1:8000/"
        )
    )

    assert (
        client._build_url(
            "/health"
        )
        == "http://127.0.0.1:8000/health"
    )


def test_ui_client_builds_scan_url():
    client = LeakGuardApiClient(
        base_url=(
            "http://localhost:9000"
        )
    )

    assert (
        client._build_url(
            "v1/scan"
        )
        == (
            "http://localhost:9000/"
            "v1/scan"
        )
    )


def test_ui_client_scan_uses_public_contract(
    monkeypatch,
):
    captured = {}

    def fake_request_json(
        self,
        *,
        method,
        path,
        payload=None,
    ):
        captured[
            "method"
        ] = method

        captured[
            "path"
        ] = path

        captured[
            "payload"
        ] = payload

        return (
            200,
            {
                "gate": "passed",
            },
        )

    monkeypatch.setattr(
        LeakGuardApiClient,
        "_request_json",
        fake_request_json,
    )

    client = LeakGuardApiClient()

    result = client.scan(
        path="project",
        staged=True,
        ml_advisory=None,
    )

    assert result == {
        "gate": "passed",
    }

    assert captured == {
        "method": "POST",
        "path": "/v1/scan",
        "payload": {
            "path": "project",
            "staged": True,
            "ml_advisory": None,
        },
    }


def test_ui_client_surfaces_api_error_envelope(
    monkeypatch,
):
    def fake_request_json(
        self,
        *,
        method,
        path,
        payload=None,
    ):
        return (
            403,
            {
                "error": {
                    "code": (
                        "path_outside_scan_root"
                    ),
                    "message": (
                        "Requested project is "
                        "outside the configured "
                        "API scan root."
                    ),
                }
            },
        )

    monkeypatch.setattr(
        LeakGuardApiClient,
        "_request_json",
        fake_request_json,
    )

    client = LeakGuardApiClient()

    with pytest.raises(
        LeakGuardApiResponseError,
        match=(
            "path_outside_scan_root"
        ),
    ):
        client.scan(
            path="../outside",
            staged=False,
            ml_advisory=False,
        )
