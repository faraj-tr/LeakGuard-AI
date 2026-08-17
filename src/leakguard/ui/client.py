import ipaddress
import json
from dataclasses import dataclass
from typing import Any
from urllib.error import (
    HTTPError,
    URLError,
)
from urllib.parse import (
    urljoin,
    urlsplit,
)
from urllib.request import (
    Request,
    urlopen,
)


DEFAULT_API_URL = (
    "http://127.0.0.1:8000"
)

DEFAULT_TIMEOUT_SECONDS = 30.0


KNOWN_API_ERROR_CODES = frozenset(
    {
        "invalid_request",
        "path_outside_scan_root",
        "project_not_found",
        "invalid_project_path",
        "invalid_configuration",
        "scan_execution_failed",
        "internal_error",
    }
)


PUBLIC_ERROR_MESSAGES = {
    "invalid_request": (
        "The scan request was rejected."
    ),
    "path_outside_scan_root": (
        "The project is outside the API "
        "scan root."
    ),
    "project_not_found": (
        "The requested project was not found."
    ),
    "invalid_project_path": (
        "The requested project path is invalid."
    ),
    "invalid_configuration": (
        "LeakGuard project configuration "
        "could not be used safely."
    ),
    "scan_execution_failed": (
        "The security scan could not be "
        "completed."
    ),
    "internal_error": (
        "The LeakGuard API encountered an "
        "internal error."
    ),
    "api_health_failed": (
        "The LeakGuard API health check "
        "failed."
    ),
    "invalid_health_response": (
        "The LeakGuard API health response "
        "was invalid."
    ),
    "api_error": (
        "The LeakGuard API rejected the "
        "request."
    ),
}


class LeakGuardApiClientError(Exception):
    """
    Base error for dashboard-to-API
    communication.
    """

    pass


class LeakGuardApiConfigurationError(
    LeakGuardApiClientError
):
    """
    Raised when the dashboard API endpoint
    violates the local-first boundary.
    """

    pass


class LeakGuardApiUnavailableError(
    LeakGuardApiClientError
):
    """
    Raised when the local LeakGuard API cannot
    be reached.
    """

    pass


class LeakGuardApiResponseError(
    LeakGuardApiClientError
):
    """
    Raised when the API response cannot be
    trusted or accepted.

    Server-provided error messages are not
    stored or reflected by this exception.
    """

    def __init__(
        self,
        code: str,
    ) -> None:
        self.code = code

        super().__init__(
            code
        )


def public_error_message(
    code: str,
) -> str:
    """
    Return dashboard-owned text for an API
    error code.
    """

    return PUBLIC_ERROR_MESSAGES.get(
        code,
        PUBLIC_ERROR_MESSAGES[
            "api_error"
        ],
    )


def normalize_local_api_url(
    base_url: str,
) -> str:
    """
    Validate the dashboard API endpoint.

    The current dashboard intentionally
    communicates only with a loopback HTTP
    service. This prevents accidental project
    path disclosure to a remote endpoint.
    """

    if (
        not isinstance(
            base_url,
            str,
        )
        or not base_url.strip()
    ):
        raise LeakGuardApiConfigurationError(
            "Invalid LeakGuard API URL."
        )

    candidate = base_url.strip()

    try:
        parsed = urlsplit(
            candidate
        )

        # Accessing .port performs additional
        # port validation.
        parsed.port

    except ValueError as error:
        raise LeakGuardApiConfigurationError(
            "Invalid LeakGuard API URL."
        ) from error

    if parsed.scheme not in {
        "http",
        "https",
    }:
        raise LeakGuardApiConfigurationError(
            "LeakGuard API URL must use HTTP "
            "or HTTPS."
        )

    if (
        parsed.username is not None
        or parsed.password is not None
    ):
        raise LeakGuardApiConfigurationError(
            "LeakGuard API URL must not "
            "contain credentials."
        )

    if (
        parsed.query
        or parsed.fragment
    ):
        raise LeakGuardApiConfigurationError(
            "LeakGuard API URL must not "
            "contain a query or fragment."
        )

    if parsed.path not in {
        "",
        "/",
    }:
        raise LeakGuardApiConfigurationError(
            "LeakGuard API URL must not "
            "contain a path."
        )

    hostname = parsed.hostname

    if hostname is None:
        raise LeakGuardApiConfigurationError(
            "LeakGuard API URL must contain "
            "a host."
        )

    normalized_host = (
        hostname
        .rstrip(".")
        .lower()
    )

    is_loopback = (
        normalized_host
        == "localhost"
    )

    if not is_loopback:
        try:
            is_loopback = (
                ipaddress.ip_address(
                    normalized_host
                ).is_loopback
            )

        except ValueError:
            is_loopback = False

    if not is_loopback:
        raise LeakGuardApiConfigurationError(
            "LeakGuard dashboard accepts only "
            "local loopback API addresses."
        )

    return candidate.rstrip(
        "/"
    )


@dataclass(frozen=True)
class LeakGuardApiClient:
    """
    Minimal HTTP client used by the dashboard.

    The UI communicates only with the public
    LeakGuard HTTP API. It never calls scanner
    internals directly.
    """

    base_url: str = DEFAULT_API_URL
    timeout_seconds: float = (
        DEFAULT_TIMEOUT_SECONDS
    )

    def __post_init__(
        self,
    ) -> None:
        normalized_url = (
            normalize_local_api_url(
                self.base_url
            )
        )

        timeout = self.timeout_seconds

        if (
            isinstance(
                timeout,
                bool,
            )
            or not isinstance(
                timeout,
                (int, float),
            )
            or timeout <= 0
        ):
            raise (
                LeakGuardApiConfigurationError(
                    "API timeout must be "
                    "positive."
                )
            )

        object.__setattr__(
            self,
            "base_url",
            normalized_url,
        )

    def _build_url(
        self,
        path: str,
    ) -> str:
        base = (
            self.base_url.rstrip("/")
            + "/"
        )

        return urljoin(
            base,
            path.lstrip("/"),
        )

    def _request_json(
        self,
        *,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any]]:
        headers = {
            "Accept": "application/json",
        }

        body = None

        if payload is not None:
            body = json.dumps(
                payload
            ).encode(
                "utf-8"
            )

            headers[
                "Content-Type"
            ] = "application/json"

        request = Request(
            self._build_url(
                path
            ),
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                status_code = (
                    response.status
                )

                raw_body = response.read()

        except HTTPError as error:
            status_code = error.code
            raw_body = error.read()

        except (
            URLError,
            TimeoutError,
            OSError,
        ) as error:
            raise (
                LeakGuardApiUnavailableError(
                    "LeakGuard API is unavailable."
                )
            ) from error

        try:
            decoded = raw_body.decode(
                "utf-8"
            )

            data = json.loads(
                decoded
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as error:
            raise (
                LeakGuardApiResponseError(
                    "api_error"
                )
            ) from error

        if not isinstance(
            data,
            dict,
        ):
            raise LeakGuardApiResponseError(
                "api_error"
            )

        return (
            status_code,
            data,
        )

    def health(
        self,
    ) -> dict[str, Any]:
        """
        Read and validate public API health
        metadata.
        """

        status_code, payload = (
            self._request_json(
                method="GET",
                path="/health",
            )
        )

        if status_code != 200:
            raise LeakGuardApiResponseError(
                "api_health_failed"
            )

        service_version = payload.get(
            "service_version"
        )

        if (
            payload.get(
                "status"
            ) != "ok"
            or payload.get(
                "service"
            ) != "leakguard-ai"
            or payload.get(
                "api_version"
            ) != "v1"
            or not isinstance(
                service_version,
                str,
            )
            or not service_version
        ):
            raise LeakGuardApiResponseError(
                "invalid_health_response"
            )

        return payload

    def scan(
        self,
        *,
        path: str,
        staged: bool,
        ml_advisory: bool | None,
    ) -> dict[str, Any]:
        """
        Submit one project scan through the
        public FastAPI contract.
        """

        status_code, payload = (
            self._request_json(
                method="POST",
                path="/v1/scan",
                payload={
                    "path": path,
                    "staged": staged,
                    "ml_advisory": (
                        ml_advisory
                    ),
                },
            )
        )

        if status_code != 200:
            code = "api_error"

            error_payload = payload.get(
                "error"
            )

            if isinstance(
                error_payload,
                dict,
            ):
                candidate_code = (
                    error_payload.get(
                        "code"
                    )
                )

                if (
                    isinstance(
                        candidate_code,
                        str,
                    )
                    and candidate_code
                    in KNOWN_API_ERROR_CODES
                ):
                    code = candidate_code

            raise LeakGuardApiResponseError(
                code
            )

        return payload
