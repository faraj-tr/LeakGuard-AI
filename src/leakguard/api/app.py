from fastapi import FastAPI

from leakguard.api.schemas import (
    HealthResponse,
)


SERVICE_NAME = "leakguard-ai"
SERVICE_VERSION = "0.1.0"
API_VERSION = "v1"


def create_app() -> FastAPI:
    """
    Build the LeakGuard AI HTTP application.

    Scanner execution is intentionally kept
    outside this foundation slice.
    """

    application = FastAPI(
        title="LeakGuard AI API",
        description=(
            "Local-first HTTP interface for "
            "LeakGuard AI security scanning."
        ),
        version=SERVICE_VERSION,
    )

    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["system"],
        summary="Check API health",
    )
    def health() -> HealthResponse:
        """
        Return a minimal, non-sensitive
        service-health response.
        """

        return HealthResponse(
            status="ok",
            service=SERVICE_NAME,
            api_version=API_VERSION,
            service_version=(
                SERVICE_VERSION
            ),
        )

    return application


app = create_app()
