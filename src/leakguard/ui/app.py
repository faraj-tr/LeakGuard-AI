import os

import streamlit as st

from leakguard.ui.client import (
    DEFAULT_API_URL,
    LeakGuardApiClient,
    LeakGuardApiClientError,
)


API_URL_ENV = "LEAKGUARD_API_URL"


def build_api_client() -> LeakGuardApiClient:
    """
    Create the dashboard HTTP client.

    The API address is configurable without
    exposing scanner internals to the UI.
    """

    api_url = os.environ.get(
        API_URL_ENV,
        DEFAULT_API_URL,
    )

    return LeakGuardApiClient(
        base_url=api_url
    )


def render_header() -> None:
    st.title(
        "LeakGuard AI"
    )

    st.caption(
        "Code fast with AI. "
        "Ship without leaking secrets."
    )


def render_api_status(
    client: LeakGuardApiClient,
) -> bool:
    """
    Display local API availability without
    exposing host filesystem information.
    """

    try:
        health = client.health()

    except LeakGuardApiClientError:
        st.error(
            "LeakGuard API is unavailable. "
            "Start the local API service "
            "before scanning."
        )

        return False

    service_version = health.get(
        "service_version",
        "unknown",
    )

    st.success(
        "LeakGuard API connected"
    )

    st.caption(
        "Service version: "
        f"{service_version}"
    )

    return True


def main() -> None:
    st.set_page_config(
        page_title="LeakGuard AI",
        page_icon="???",
        layout="wide",
    )

    render_header()

    client = build_api_client()

    api_available = (
        render_api_status(
            client
        )
    )

    st.divider()

    st.subheader(
        "Security Scan"
    )

    if not api_available:
        st.info(
            "Scanning controls will become "
            "available when the local API "
            "service is running."
        )

        return

    st.info(
        "Dashboard connection established. "
        "The scan workflow will be added in "
        "the next UI slice."
    )


if __name__ == "__main__":
    main()
