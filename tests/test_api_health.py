from fastapi.testclient import (
    TestClient,
)

from leakguard.api.app import app


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
        "service_version": "0.1.0",
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
        == "0.1.0"
    )

    assert "/health" in (
        schema["paths"]
    )
