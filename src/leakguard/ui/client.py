import json
from dataclasses import dataclass
from typing import Any
from urllib.error import (
    HTTPError,
    URLError,
)
from urllib.parse import urljoin
from urllib.request import (
    Request,
    urlopen,
)


DEFAULT_API_URL = (
    "http://127.0.0.1:8000"
)

DEFAULT_TIMEOUT_SECONDS = 30.0


class LeakGuardApiClientError(Exception):
    """
    Base error for dashboard-to-API
    communication.
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
    Raised when the API returns an unexpected
    or malformed response.
    """

    pass


@dataclass(frozen=True)
class LeakGuardApiClient:
    """
    Minimal HTTP client used by the dashboard.

    The UI communicates only with the public
    LeakGuard HTTP API. It does not call
    scanner internals directly.
    """

    base_url: str = DEFAULT_API_URL
    timeout_seconds: float = (
        DEFAULT_TIMEOUT_SECONDS
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
            decoded = (
                raw_body.decode(
                    "utf-8"
                )
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
                    "LeakGuard API returned an "
                    "invalid JSON response."
                )
            ) from error

        if not isinstance(
            data,
            dict,
        ):
            raise LeakGuardApiResponseError(
                "LeakGuard API returned an "
                "unexpected response shape."
            )

        return (
            status_code,
            data,
        )

    def health(
        self,
    ) -> dict[str, Any]:
        """
        Read public API health metadata.
        """

        status_code, payload = (
            self._request_json(
                method="GET",
                path="/health",
            )
        )

        if status_code != 200:
            raise LeakGuardApiResponseError(
                "LeakGuard API health check "
                "failed."
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
            error = payload.get(
                "error"
            )

            if isinstance(
                error,
                dict,
            ):
                code = str(
                    error.get(
                        "code",
                        "api_error",
                    )
                )

                message = str(
                    error.get(
                        "message",
                        (
                            "LeakGuard API "
                            "rejected the scan."
                        ),
                    )
                )

                raise (
                    LeakGuardApiResponseError(
                        f"{code}: {message}"
                    )
                )

            raise LeakGuardApiResponseError(
                "LeakGuard API rejected the "
                "scan."
            )

        return payload
