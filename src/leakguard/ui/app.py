import os

import streamlit as st

from leakguard.ui.client import (
    DEFAULT_API_URL,
    LeakGuardApiClient,
    LeakGuardApiClientError,
    LeakGuardApiConfigurationError,
    LeakGuardApiResponseError,
    public_error_message,
)
from leakguard.ui.components import (
    LOGO_PATH,
    inject_component_styles,
    render_api_unavailable,
    render_brand_header,
    render_findings as render_findings_component,
    render_gate_summary,
    render_page_intro,
    render_scan_form,
    render_sidebar,
)
from leakguard.ui.styles import (
    inject_global_styles,
)
from leakguard.ui.workflow import (
    DashboardPayloadError,
    ScanView,
    build_scan_view,
    resolve_ml_override,
)


API_URL_ENV = "LEAKGUARD_API_URL"

LAST_SCAN_RESULT_KEY = (
    "leakguard_last_scan_result"
)

API_SERVICE_VERSION_KEY = (
    "leakguard_api_service_version"
)

SIDEBAR_SCAN_FLASH_KEY = (
    "leakguard_sidebar_scan_flash"
)


def build_api_client() -> LeakGuardApiClient:
    """
    Create the dashboard HTTP client.
    """

    api_url = os.environ.get(
        API_URL_ENV,
        DEFAULT_API_URL,
    )

    return LeakGuardApiClient(
        base_url=api_url
    )


def render_header(
    *,
    api_connected: bool = False,
    service_version: str | None = None,
) -> None:
    """
    Compatibility wrapper for the redesigned
    product header.
    """

    render_brand_header(
        api_connected=api_connected,
        service_version=service_version,
    )


def render_api_status(
    client: LeakGuardApiClient,
) -> bool:
    """
    Probe local API availability.

    Successful health information is rendered
    by the redesigned header and sidebar rather
    than by Streamlit's default success box.
    """

    try:
        health = client.health()

    except LeakGuardApiResponseError as error:
        st.session_state.pop(
            API_SERVICE_VERSION_KEY,
            None,
        )

        st.error(
            "LeakGuard API health check "
            "failed."
        )

        st.caption(
            public_error_message(
                error.code
            )
        )

        return False

    except LeakGuardApiClientError:
        st.session_state.pop(
            API_SERVICE_VERSION_KEY,
            None,
        )

        st.error(
            "LeakGuard API is unavailable. "
            "Start the local API service "
            "before scanning."
        )

        return False

    service_version = health[
        "service_version"
    ]

    st.session_state[
        API_SERVICE_VERSION_KEY
    ] = str(service_version)

    return True


def run_scan_from_form(
    client: LeakGuardApiClient,
) -> None:
    """
    Collect scan controls from the redesigned
    UI and submit one scan through the public
    local HTTP API.
    """

    submission = render_scan_form()

    if submission is None:
        return

    normalized_path = (
        submission.project_path.strip()
    )

    if not normalized_path:
        st.error(
            "Scan path is required."
        )

        return

    ml_override = resolve_ml_override(
        submission.ml_policy
    )

    try:
        with st.spinner(
            "Running LeakGuard security scan..."
        ):
            payload = client.scan(
                path=normalized_path,
                staged=submission.staged,
                ml_advisory=ml_override,
            )

    except LeakGuardApiResponseError as error:
        st.error(
            "Security scan could not be "
            "completed."
        )

        st.caption(
            public_error_message(
                error.code
            )
        )

        return

    except LeakGuardApiClientError:
        st.error(
            "Security scan could not be "
            "completed because the local API "
            "is unavailable."
        )

        return

    try:
        scan_view = build_scan_view(
            payload
        )

    except DashboardPayloadError:
        st.error(
            "LeakGuard API returned a response "
            "that could not be displayed "
            "safely."
        )

        return

    st.session_state[
        LAST_SCAN_RESULT_KEY
    ] = scan_view

    # One-shot UI feedback. The next rerun
    # renders the Security Scan navigation item
    # in green with a short pulse animation.
    st.session_state[
        SIDEBAR_SCAN_FLASH_KEY
    ] = True

    st.rerun()


def render_scan_summary(
    scan_view: ScanView,
) -> None:
    """
    Compatibility wrapper around the new
    security gate component.
    """

    render_gate_summary(
        scan_view
    )


def render_findings(
    scan_view: ScanView,
) -> None:
    """
    Compatibility wrapper around the new
    findings presentation.
    """

    render_findings_component(
        scan_view
    )


def render_ready_state() -> None:
    """
    Render the calm pre-scan state.
    """

    st.html(
        """
<div class="lg-state-panel">
    <strong>Ready for inspection.</strong>
    Choose a scan target and run LeakGuard.
    Processing stays behind the configured
    local API boundary, and public finding
    output remains masked.
</div>
"""
    )


def main() -> None:
    st.set_page_config(
        page_title="LeakGuard AI",
        page_icon=str(LOGO_PATH),
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_global_styles()
    inject_component_styles()

    try:
        client = build_api_client()

    except LeakGuardApiConfigurationError:
        st.session_state.pop(
            API_SERVICE_VERSION_KEY,
            None,
        )

        st.session_state.pop(
            LAST_SCAN_RESULT_KEY,
            None,
        )

        render_sidebar(
            api_connected=False,
        )

        render_header(
            api_connected=False,
        )

        render_page_intro()

        st.error(
            "LeakGuard API URL configuration "
            "is unsafe."
        )

        st.caption(
            "The dashboard accepts only local "
            "loopback API addresses."
        )

        return

    api_available = render_api_status(
        client
    )

    service_version = (
        st.session_state.get(
            API_SERVICE_VERSION_KEY
        )
    )

    sidebar_scan_flash = bool(
        st.session_state.pop(
            SIDEBAR_SCAN_FLASH_KEY,
            False,
        )
    )

    render_sidebar(
        api_connected=api_available,
        scan_recently_run=(
            sidebar_scan_flash
        ),
    )

    render_header(
        api_connected=api_available,
        service_version=(
            service_version
            if isinstance(
                service_version,
                str,
            )
            else None
        ),
    )

    render_page_intro()

    if not api_available:
        st.session_state.pop(
            LAST_SCAN_RESULT_KEY,
            None,
        )

        render_api_unavailable()

        return

    run_scan_from_form(
        client
    )

    scan_view = (
        st.session_state.get(
            LAST_SCAN_RESULT_KEY
        )
    )

    if isinstance(
        scan_view,
        ScanView,
    ):
        render_scan_summary(
            scan_view
        )

        render_findings(
            scan_view
        )

    else:
        render_ready_state()


if __name__ == "__main__":
    main()