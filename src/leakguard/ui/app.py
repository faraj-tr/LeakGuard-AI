import os

import streamlit as st

from leakguard.ui.client import (
    DEFAULT_API_URL,
    LeakGuardApiClient,
    LeakGuardApiClientError,
)
from leakguard.ui.workflow import (
    DashboardPayloadError,
    ML_POLICY_CHOICES,
    ScanView,
    build_scan_view,
    resolve_ml_override,
)


API_URL_ENV = "LEAKGUARD_API_URL"

LAST_SCAN_RESULT_KEY = (
    "leakguard_last_scan_result"
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

    st.text(
        "Service version: "
        f"{service_version}"
    )

    return True


def run_scan_from_form(
    client: LeakGuardApiClient,
) -> None:
    """
    Render scan controls and submit one scan
    through the public HTTP API.
    """

    with st.form(
        "leakguard_scan_form"
    ):
        project_path = st.text_input(
            "Project path",
            value=".",
            help=(
                "Path must be inside the "
                "FastAPI scan root."
            ),
        )

        staged = st.checkbox(
            "Scan staged Git content only",
            value=False,
            help=(
                "Inspect the Git index instead "
                "of working-tree content."
            ),
        )

        ml_policy = st.selectbox(
            "Candidate v2 ML advisory",
            options=ML_POLICY_CHOICES,
            index=0,
            help=(
                "Candidate v2 is experimental "
                "and never has independent "
                "blocking authority."
            ),
        )

        submitted = (
            st.form_submit_button(
                "Run Security Scan"
            )
        )

    if not submitted:
        return

    normalized_path = (
        project_path.strip()
    )

    if not normalized_path:
        st.error(
            "Project path is required."
        )

        return

    ml_override = (
        resolve_ml_override(
            ml_policy
        )
    )

    try:
        with st.spinner(
            "Running LeakGuard security scan..."
        ):
            payload = client.scan(
                path=normalized_path,
                staged=staged,
                ml_advisory=(
                    ml_override
                ),
            )

    except LeakGuardApiClientError as error:
        st.error(
            "Security scan could not be "
            "completed."
        )

        st.text(
            str(
                error
            )
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


def render_scan_summary(
    scan_view: ScanView,
) -> None:
    """
    Render gate status and aggregate metrics.
    """

    st.subheader(
        "Scan Result"
    )

    if scan_view.gate == "passed":
        st.success(
            "Security gate passed. "
            "No findings were reported."
        )

    else:
        st.error(
            "Security gate failed. "
            "Review the findings before "
            "shipping."
        )

    summary_columns = st.columns(
        3
    )

    summary_columns[0].metric(
        "Gate",
        scan_view.gate.upper(),
    )

    summary_columns[1].metric(
        "Files scanned",
        scan_view.files_scanned,
    )

    summary_columns[2].metric(
        "Findings",
        scan_view.findings_count,
    )

    severity_columns = st.columns(
        4
    )

    severity_columns[0].metric(
        "Critical",
        scan_view.severity.critical,
    )

    severity_columns[1].metric(
        "High",
        scan_view.severity.high,
    )

    severity_columns[2].metric(
        "Medium",
        scan_view.severity.medium,
    )

    severity_columns[3].metric(
        "Low",
        scan_view.severity.low,
    )

    mode_text = (
        "Staged Git index"
        if scan_view.mode == "staged"
        else "Working project"
    )

    ml_text = (
        "Enabled ? experimental, "
        "non-blocking"
        if scan_view.ml_advisory_enabled
        else "Disabled"
    )

    st.text(
        f"Scan mode: {mode_text}"
    )

    st.text(
        "Candidate v2 advisory: "
        f"{ml_text}"
    )


def render_findings(
    scan_view: ScanView,
) -> None:
    """
    Render only fields accepted by the strict
    dashboard view model.
    """

    if not scan_view.findings:
        return

    st.subheader(
        "Findings"
    )

    for index, finding in enumerate(
        scan_view.findings,
        start=1,
    ):
        label = (
            f"Finding {index} "
            f"? {finding.severity}"
        )

        with st.expander(
            label,
            expanded=(
                index == 1
            ),
        ):
            st.text(
                "Type: "
                f"{finding.finding_type}"
            )

            st.text(
                "File: "
                f"{finding.file}"
            )

            st.text(
                "Line: "
                f"{finding.line}"
            )

            st.text(
                "Masked value: "
                f"{finding.masked_value}"
            )

            if (
                finding.framework
                is not None
            ):
                st.text(
                    "Framework: "
                    f"{finding.framework}"
                )

            if (
                finding.candidate_score
                is not None
            ):
                st.text(
                    "Heuristic candidate "
                    "score: "
                    f"{finding.candidate_score}"
                )

            if finding.reasons:
                st.text(
                    "Reasons:"
                )

                for reason in (
                    finding.reasons
                ):
                    st.text(
                        f"- {reason}"
                    )

            advisory = (
                finding.ml_advisory
            )

            if advisory is not None:
                st.divider()

                st.text(
                    "Candidate v2 advisory"
                )

                st.text(
                    "Prediction: "
                    f"{advisory.prediction}"
                )

                st.text(
                    "Risk score: "
                    f"{advisory.risk_score:.3f}"
                )

                st.text(
                    "Threshold: "
                    f"{advisory.threshold:.3f}"
                )

                st.caption(
                    "Experimental advisory "
                    "signal only. The risk "
                    "score is not a calibrated "
                    "probability and does not "
                    "have blocking authority."
                )


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
        st.session_state.pop(
            LAST_SCAN_RESULT_KEY,
            None,
        )

        st.info(
            "Scanning controls will become "
            "available when the local API "
            "service is running."
        )

        return

    st.caption(
        "The HTTP API restricts scanning to "
        "its configured scan root."
    )

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
        st.divider()

        render_scan_summary(
            scan_view
        )

        render_findings(
            scan_view
        )


if __name__ == "__main__":
    main()
