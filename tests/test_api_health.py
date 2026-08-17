from fastapi.testclient import (
    TestClient,
)

from leakguard.api.app import app
from leakguard.version import __version__


client = TestClient(
    app
)


def test_health_endpoint():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "service": "leakguard-ai",
        "api_version": "v1",
        "service_version": __version__,
    }


def test_openapi_contract_exposes_health():
    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    schema = response.json()

    assert (
        schema["info"]["title"]
        == "LeakGuard AI API"
    )

    assert (
        schema["info"]["version"]
        == __version__
    )

    assert "/health" in (
        schema["paths"]
    )
