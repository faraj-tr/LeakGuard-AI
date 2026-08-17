from pathlib import Path

from fastapi import (
    FastAPI,
    HTTPException,
)

from leakguard.api.schemas import (
    HealthResponse,
    ScanRequest,
    ScanResponse,
    SeverityCounts,
)
from leakguard.service import (
    ProjectPathNotFoundError,
    ProjectPathTypeError,
    ScanConfigurationError,
    ScanExecutionError,
    run_security_scan,
)


SERVICE_NAME = "leakguard-ai"
SERVICE_VERSION = "0.1.0"
API_VERSION = "v1"


def create_app() -> FastAPI:
    """
    Build the LeakGuard AI HTTP application.
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

    @application.post(
        "/v1/scan",
        response_model=ScanResponse,
        tags=["scanning"],
        summary=(
            "Scan a local project"
        ),
    )
    def scan_project(
        request: ScanRequest,
    ) -> ScanResponse:
        """
        Run LeakGuard against a local project
        and return structured, masked findings.
        """

        try:
            result = run_security_scan(
                Path(
                    request.path
                ),
                staged=request.staged,
                ml_advisory_override=(
                    request.ml_advisory
                ),
            )

        except (
            ProjectPathNotFoundError
        ) as error:
            raise HTTPException(
                status_code=404,
                detail=str(
                    error
                ),
            ) from error

        except (
            ProjectPathTypeError
        ) as error:
            raise HTTPException(
                status_code=400,
                detail=str(
                    error
                ),
            ) from error

        except (
            ScanConfigurationError,
            ScanExecutionError,
        ) as error:
            raise HTTPException(
                status_code=400,
                detail=str(
                    error
                ),
            ) from error

        return ScanResponse(
            mode=result.mode,
            files_scanned=(
                result.files_scanned
            ),
            findings_count=(
                result.findings_count
            ),
            gate=result.gate,
            ml_advisory_enabled=(
                result.ml_advisory_enabled
            ),
            severity_counts=(
                SeverityCounts(
                    critical=(
                        result.critical_count
                    ),
                    high=(
                        result.high_count
                    ),
                    medium=(
                        result.medium_count
                    ),
                    low=(
                        result.low_count
                    ),
                )
            ),
            findings=result.findings,
        )

    return application


app = create_app()
