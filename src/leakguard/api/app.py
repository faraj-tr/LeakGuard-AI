from pathlib import Path

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.exceptions import (
    RequestValidationError,
)
from fastapi.responses import (
    JSONResponse,
)

from leakguard.api.schemas import (
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    ScanRequest,
    ScanResponse,
    SeverityCounts,
)
from leakguard.api.security import (
    ApiPathBoundaryError,
    get_api_scan_root,
    resolve_api_project_path,
)
from leakguard.service import (
    ProjectPathNotFoundError,
    ProjectPathTypeError,
    ScanConfigurationError,
    ScanExecutionError,
    run_security_scan,
)
from leakguard.version import __version__


SERVICE_NAME = "leakguard-ai"
SERVICE_VERSION = __version__
API_VERSION = "v1"


SCAN_ERROR_RESPONSES = {
    400: {
        "model": ErrorResponse,
        "description": (
            "Invalid project path or "
            "LeakGuard configuration."
        ),
    },
    403: {
        "model": ErrorResponse,
        "description": (
            "Requested path is outside the "
            "configured API scan root."
        ),
    },
    404: {
        "model": ErrorResponse,
        "description": (
            "Requested project does not exist."
        ),
    },
    409: {
        "model": ErrorResponse,
        "description": (
            "The requested scan cannot run "
            "in the current project state."
        ),
    },
    422: {
        "model": ErrorResponse,
        "description": (
            "Request validation failed."
        ),
    },
    500: {
        "model": ErrorResponse,
        "description": (
            "Unexpected internal failure."
        ),
    },
}


def build_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    """
    Build the stable, non-sensitive API error
    envelope.
    """

    payload = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(),
    )


def create_app(
    scan_root: Path | None = None,
) -> FastAPI:
    """
    Build the LeakGuard AI HTTP application.

    HTTP filesystem access is restricted to
    the configured scan root.
    """

    resolved_scan_root = (
        get_api_scan_root(
            scan_root
        )
    )

    application = FastAPI(
        title="LeakGuard AI API",
        description=(
            "Local-first HTTP interface for "
            "LeakGuard AI security scanning."
        ),
        version=SERVICE_VERSION,
    )

    @application.exception_handler(
        RequestValidationError
    )
    async def validation_error_handler(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        """
        Do not reflect malformed request data
        or validation internals back to HTTP
        clients.
        """

        return build_error_response(
            status_code=422,
            code="invalid_request",
            message=(
                "Request validation failed."
            ),
        )

    @application.exception_handler(
        ApiPathBoundaryError
    )
    async def path_boundary_handler(
        request: Request,
        error: ApiPathBoundaryError,
    ) -> JSONResponse:
        return build_error_response(
            status_code=403,
            code="path_outside_scan_root",
            message=(
                "Requested project is outside "
                "the configured API scan root."
            ),
        )

    @application.exception_handler(
        ProjectPathNotFoundError
    )
    async def project_missing_handler(
        request: Request,
        error: ProjectPathNotFoundError,
    ) -> JSONResponse:
        return build_error_response(
            status_code=404,
            code="project_not_found",
            message=(
                "Project path does not exist."
            ),
        )

    @application.exception_handler(
        ProjectPathTypeError
    )
    async def project_type_handler(
        request: Request,
        error: ProjectPathTypeError,
    ) -> JSONResponse:
        return build_error_response(
            status_code=400,
            code="invalid_project_path",
            message=(
                "Project path must be a "
                "directory."
            ),
        )

    @application.exception_handler(
        ScanConfigurationError
    )
    async def configuration_error_handler(
        request: Request,
        error: ScanConfigurationError,
    ) -> JSONResponse:
        return build_error_response(
            status_code=400,
            code="invalid_configuration",
            message=(
                "LeakGuard configuration "
                "could not be used safely."
            ),
        )

    @application.exception_handler(
        ScanExecutionError
    )
    async def execution_error_handler(
        request: Request,
        error: ScanExecutionError,
    ) -> JSONResponse:
        return build_error_response(
            status_code=409,
            code="scan_execution_failed",
            message=(
                "Security scan could not be "
                "completed."
            ),
        )

    @application.exception_handler(
        Exception
    )
    async def internal_error_handler(
        request: Request,
        error: Exception,
    ) -> JSONResponse:
        """
        Unexpected exception details are never
        reflected to clients.
        """

        return build_error_response(
            status_code=500,
            code="internal_error",
            message=(
                "Internal server error."
            ),
        )

    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["system"],
        summary="Check API health",
    )
    def health() -> HealthResponse:
        """
        Return minimal non-sensitive service
        health metadata.
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
        responses=SCAN_ERROR_RESPONSES,
        tags=["scanning"],
        summary="Scan a local project",
    )
    def scan_project(
        scan_request: ScanRequest,
    ) -> ScanResponse:
        """
        Run LeakGuard against a project inside
        the configured HTTP scan boundary.
        """

        project_path = (
            resolve_api_project_path(
                requested_path=(
                    scan_request.path
                ),
                scan_root=(
                    resolved_scan_root
                ),
            )
        )

        result = run_security_scan(
            project_path,
            staged=scan_request.staged,
            ml_advisory_override=(
                scan_request.ml_advisory
            ),
        )

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
