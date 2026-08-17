from leakguard.ui.client import (
    LeakGuardApiClient,
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
