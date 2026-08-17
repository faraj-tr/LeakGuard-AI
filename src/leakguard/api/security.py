import os
from pathlib import Path


API_SCAN_ROOT_ENV = (
    "LEAKGUARD_API_SCAN_ROOT"
)


class ApiScanRootError(RuntimeError):
    """
    Raised when the API scan root cannot be
    configured safely.
    """

    pass


class ApiPathBoundaryError(Exception):
    """
    Raised when an HTTP scan request attempts
    to leave the configured API scan root.
    """

    pass


def get_api_scan_root(
    explicit_root: Path | None = None,
) -> Path:
    """
    Resolve the filesystem boundary available
    to HTTP scan requests.

    Priority:
    1. Explicit application-factory root.
    2. LEAKGUARD_API_SCAN_ROOT.
    3. Current working directory.

    The resolved root itself is never returned
    by API responses.
    """

    if explicit_root is not None:
        candidate = Path(
            explicit_root
        )

    else:
        configured_root = (
            os.environ.get(
                API_SCAN_ROOT_ENV
            )
        )

        if configured_root:
            candidate = Path(
                configured_root
            )

        else:
            candidate = Path.cwd()

    try:
        resolved_root = (
            candidate
            .expanduser()
            .resolve()
        )

    except OSError as error:
        raise ApiScanRootError(
            "API scan root could not be "
            "resolved safely."
        ) from error

    if not resolved_root.exists():
        raise ApiScanRootError(
            "API scan root must exist."
        )

    if not resolved_root.is_dir():
        raise ApiScanRootError(
            "API scan root must be a "
            "directory."
        )

    return resolved_root


def resolve_api_project_path(
    requested_path: str,
    scan_root: Path,
) -> Path:
    """
    Resolve one requested project path while
    enforcing containment inside scan_root.

    Relative paths are interpreted relative
    to the configured API scan root.

    Resolution also prevents ordinary '..'
    traversal and symlink-based escapes from
    crossing the HTTP filesystem boundary.
    """

    requested = Path(
        requested_path
    ).expanduser()

    if requested.is_absolute():
        candidate = requested

    else:
        candidate = (
            scan_root
            / requested
        )

    try:
        resolved = (
            candidate.resolve()
        )

    except OSError as error:
        raise ApiPathBoundaryError(
            "Requested project path could "
            "not be resolved safely."
        ) from error

    try:
        resolved.relative_to(
            scan_root
        )

    except ValueError as error:
        raise ApiPathBoundaryError(
            "Requested project is outside "
            "the configured API scan root."
        ) from error

    return resolved
