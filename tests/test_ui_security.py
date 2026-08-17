import ast
from pathlib import Path

import pytest

from leakguard.ui.client import (
    LeakGuardApiClient,
    LeakGuardApiConfigurationError,
    LeakGuardApiResponseError,
)


def test_ui_client_rejects_remote_api_url():
    with pytest.raises(
        LeakGuardApiConfigurationError,
        match="loopback",
    ):
        LeakGuardApiClient(
            base_url=(
                "https://example.com"
            )
        )


def test_ui_client_rejects_url_credentials():
    with pytest.raises(
        LeakGuardApiConfigurationError,
        match="credentials",
    ):
        LeakGuardApiClient(
            base_url=(
                "http://user:pass@"
                "127.0.0.1:8000"
            )
        )


def test_ui_client_rejects_api_base_path():
    with pytest.raises(
        LeakGuardApiConfigurationError,
        match="contain a path",
    ):
        LeakGuardApiClient(
            base_url=(
                "http://127.0.0.1:8000/api"
            )
        )


def test_ui_client_accepts_ipv6_loopback():
    client = LeakGuardApiClient(
        base_url=(
            "http://[::1]:8000"
        )
    )

    assert (
        client.base_url
        == "http://[::1]:8000"
    )


def test_ui_client_rejects_nonpositive_timeout():
    with pytest.raises(
        LeakGuardApiConfigurationError,
        match="timeout",
    ):
        LeakGuardApiClient(
            timeout_seconds=0
        )


def test_ui_client_does_not_reflect_api_message(
    monkeypatch,
):
    secret = (
        "LEAKGUARD_FAKE_SERVER_SECRET_123"
    )

    def fake_request_json(
        self,
        *,
        method,
        path,
        payload=None,
    ):
        return (
            500,
            {
                "error": {
                    "code": "internal_error",
                    "message": secret,
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
        LeakGuardApiResponseError
    ) as captured:
        client.scan(
            path=".",
            staged=False,
            ml_advisory=False,
        )

    error = captured.value

    assert (
        error.code
        == "internal_error"
    )

    assert secret not in str(
        error
    )


def test_ui_health_rejects_wrong_contract(
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
            200,
            {
                "status": "ok",
                "service": "other-service",
                "api_version": "v1",
                "service_version": "0.1.0",
            },
        )

    monkeypatch.setattr(
        LeakGuardApiClient,
        "_request_json",
        fake_request_json,
    )

    client = LeakGuardApiClient()

    with pytest.raises(
        LeakGuardApiResponseError
    ) as captured:
        client.health()

    assert (
        captured.value.code
        == "invalid_health_response"
    )


def test_ui_does_not_import_scanner_internals():
    project_root = (
        Path(__file__)
        .resolve()
        .parents[1]
    )

    ui_root = (
        project_root
        / "src"
        / "leakguard"
        / "ui"
    )

    disallowed_prefixes = (
        "leakguard.service",
        "leakguard.scanner",
        "leakguard.staged",
        "leakguard.artifacts",
    )

    imported_modules = []

    for filename in (
        "app.py",
        "client.py",
        "workflow.py",
    ):
        source = (
            ui_root
            / filename
        ).read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source
        )

        for node in ast.walk(
            tree
        ):
            if isinstance(
                node,
                ast.Import,
            ):
                imported_modules.extend(
                    alias.name
                    for alias in node.names
                )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                if node.module:
                    imported_modules.append(
                        node.module
                    )

    assert not any(
        module.startswith(
            disallowed_prefixes
        )
        for module in imported_modules
    )
