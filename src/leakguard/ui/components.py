from pathlib import Path
import base64
from dataclasses import dataclass

import streamlit as st

from leakguard.ui.styles import escape_ui_text
from leakguard.ui.theme import (
    THEME,
    gate_style,
    severity_style,
)
from leakguard.ui.workflow import (
    FindingView,
    ML_POLICY_CHOICES,
    ScanView,
)


ASSETS_DIR = (
    Path(__file__).resolve().parent
    / "assets"
)

LOGO_PATH = (
    ASSETS_DIR
    / "leakguard-logo.png"
)


def logo_data_uri() -> str:
    """
    Return the bundled LeakGuard PNG as a
    browser-safe data URI.
    """

    encoded = base64.b64encode(
        LOGO_PATH.read_bytes()
    ).decode("ascii")

    return (
        "data:image/png;base64,"
        + encoded
    )


@dataclass(frozen=True)
class ScanFormSubmission:
    """
    Presentation-only scan form values.

    Scanner execution remains behind the
    local HTTP API boundary.
    """

    project_path: str
    staged: bool
    ml_policy: str


def build_component_css() -> str:
    """
    Build LeakGuard component-level styles.
    """

    return f"""
<style>

.lg-brandbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;

    padding: 0.95rem 1.05rem;
    margin-bottom: 2rem;

    background: {THEME.surface};
    border: 1px solid {THEME.border};
    border-radius: {THEME.radius_large};
}}

.lg-brand-left {{
    display: flex;
    align-items: center;
    gap: 0.8rem;
}}

.lg-brand-mark {{
    width: 2.55rem;
    height: 2.55rem;
    flex: 0 0 2.55rem;

    display: flex;
    align-items: center;
    justify-content: center;

    background: {THEME.brand};
    border-radius: 9px;

    color: #111827;
    font-family: var(--lg-mono-font);
    font-size: 0.72rem;
    font-weight: 800;
}}

.lg-brand-title {{
    color: {THEME.text_primary};
    font-family: var(--lg-heading-font);

    font-size: 1.12rem;
    font-weight: 700;
    line-height: 1.2;
    letter-spacing: -0.025em;
}}

.lg-api-status {{
    display: flex;
    align-items: center;
    gap: 0.38rem;

    margin-top: 0.22rem;

    color: {THEME.text_secondary};
    font-family: var(--lg-mono-font);
    font-size: 0.68rem;
}}

.lg-api-dot {{
    width: 0.46rem;
    height: 0.46rem;
    display: inline-block;

    border-radius: 999px;
    background: {THEME.brand};
}}

.lg-api-dot-offline {{
    background: {THEME.critical};
}}

.lg-product-chip {{
    padding: 0.42rem 0.7rem;

    background: {THEME.surface_subtle};
    border: 1px solid {THEME.border};
    border-radius: 999px;

    color: {THEME.text_secondary};
    font-family: var(--lg-mono-font);

    font-size: 0.62rem;
    font-weight: 700;

    text-transform: uppercase;
    letter-spacing: 0.08em;
}}


.lg-page-intro {{
    margin: 0.2rem 0 1.65rem;
}}

.lg-page-intro h1 {{
    margin: 0 0 0.5rem;

    color: {THEME.text_primary};
    font-family: var(--lg-heading-font);

    font-size: 2.55rem;
    font-weight: 700;
    line-height: 1.05;

    letter-spacing: -0.045em;
}}

.lg-page-intro p {{
    max-width: 52rem;
    margin: 0;

    color: {THEME.text_secondary};

    font-size: 1.02rem;
    line-height: 1.6;
}}


.lg-form-divider {{
    height: 1px;
    margin: 1.2rem 0 1rem;

    background: #F0F1F2;
}}

.lg-control-context {{
    min-height: 4.2rem;

    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: center;

    gap: 0.3rem;
    margin: 0;

    color: {THEME.text_secondary};

    font-size: 0.76rem;
    text-align: right;
}}


.lg-gate-card {{
    position: relative;
    overflow: hidden;

    margin: 1.8rem 0 2rem;
    padding: 2.5rem 1.8rem 2.1rem;

    background: {THEME.surface};
    border: 1px solid {THEME.border};
    border-radius: {THEME.radius_large};

    text-align: center;
}}

.lg-gate-accent {{
    position: absolute;

    top: 0;
    left: 0;
    right: 0;

    height: 3px;
}}

.lg-gate-label {{
    color: {THEME.text_secondary};
    font-family: var(--lg-mono-font);

    font-size: 0.68rem;
    font-weight: 700;

    text-transform: uppercase;
    letter-spacing: 0.17em;
}}

.lg-gate-state {{
    margin: 0.65rem 0 0.6rem;

    font-family: var(--lg-heading-font);

    font-size: clamp(3.3rem, 7vw, 4.8rem);
    font-weight: 750;
    line-height: 1;

    letter-spacing: -0.055em;
}}

.lg-gate-copy {{
    max-width: 42rem;
    margin: 0 auto;

    color: {THEME.text_secondary};

    font-size: 0.96rem;
    line-height: 1.55;
}}

.lg-metric-grid {{
    display: grid;
    grid-template-columns:
        repeat(6, minmax(0, 1fr));

    gap: 1rem;

    max-width: 58rem;
    margin: 2rem auto 0;
}}

.lg-metric-value {{
    display: block;

    color: {THEME.text_primary};
    font-family: var(--lg-heading-font);

    font-size: 1.7rem;
    font-weight: 700;
    line-height: 1.1;
}}

.lg-metric-name {{
    display: block;
    margin-top: 0.35rem;

    color: {THEME.text_secondary};
    font-family: var(--lg-mono-font);

    font-size: 0.59rem;
    font-weight: 700;

    text-transform: uppercase;
    letter-spacing: 0.08em;
}}


.lg-findings-header {{
    display: flex;
    align-items: end;
    justify-content: space-between;

    gap: 1rem;

    margin: 2rem 0 0.8rem;
}}

.lg-findings-header h2 {{
    margin: 0;
    font-size: 1.4rem;
}}

.lg-findings-header span {{
    color: {THEME.text_secondary};
    font-size: 0.78rem;
}}

.lg-finding-detail {{
    padding: 0.2rem 0 0.5rem;
}}

.lg-finding-summary {{
    display: grid;
    grid-template-columns:
        minmax(0, 1fr) auto;

    gap: 1rem;
    align-items: start;

    margin-bottom: 1.1rem;
}}

.lg-severity {{
    display: inline-flex;
    align-items: center;

    width: fit-content;

    margin-bottom: 0.55rem;
    padding: 0.26rem 0.48rem;

    border-radius: 999px;

    font-family: var(--lg-mono-font);

    font-size: 0.59rem;
    font-weight: 700;

    text-transform: uppercase;
    letter-spacing: 0.07em;
}}

.lg-finding-type {{
    color: {THEME.text_primary};

    font-size: 1rem;
    font-weight: 650;
}}

.lg-finding-location {{
    margin-top: 0.3rem;

    color: {THEME.text_secondary};
    font-family: var(--lg-mono-font);

    font-size: 0.74rem;
}}

.lg-masked-value {{
    color: {THEME.text_primary};
    font-family: var(--lg-mono-font);

    font-size: 0.74rem;
    text-align: right;

    overflow-wrap: anywhere;
}}

.lg-evidence-grid {{
    display: grid;
    grid-template-columns:
        minmax(0, 2fr)
        minmax(15rem, 1fr);

    gap: 1rem;
}}

.lg-evidence-panel {{
    min-width: 0;
    padding: 1rem;

    background: {THEME.surface_subtle};
    border: 1px solid {THEME.border};
    border-radius: {THEME.radius};
}}

.lg-section-label {{
    display: block;
    margin-bottom: 0.7rem;

    color: {THEME.text_secondary};
    font-family: var(--lg-mono-font);

    font-size: 0.61rem;
    font-weight: 700;

    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

.lg-reason-list {{
    margin: 0;
    padding-left: 1.15rem;

    color: {THEME.text_primary};

    font-size: 0.84rem;
    line-height: 1.6;
}}

.lg-fact-row {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;

    gap: 1rem;
    padding: 0.46rem 0;

    border-bottom:
        1px solid {THEME.border};
}}

.lg-fact-row:last-child {{
    border-bottom: none;
}}

.lg-fact-name {{
    color: {THEME.text_secondary};
    font-size: 0.75rem;
}}

.lg-fact-value {{
    color: {THEME.text_primary};
    font-family: var(--lg-mono-font);

    font-size: 0.73rem;
    text-align: right;

    overflow-wrap: anywhere;
}}


.lg-advisory-panel {{
    padding: 1rem;

    background: {THEME.advisory_soft};
    border: 1px solid {THEME.border};
    border-radius: {THEME.radius};
}}

.lg-advisory-title {{
    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 0.8rem;
    margin-bottom: 0.75rem;
}}

.lg-advisory-name {{
    color: {THEME.advisory};
    font-family: var(--lg-mono-font);

    font-size: 0.63rem;
    font-weight: 700;

    text-transform: uppercase;
    letter-spacing: 0.07em;
}}

.lg-advisory-chip {{
    color: {THEME.advisory};
    font-family: var(--lg-mono-font);

    font-size: 0.57rem;
    text-transform: uppercase;
}}

.lg-advisory-footer {{
    margin-top: 0.8rem;
    padding-top: 0.7rem;

    border-top:
        1px solid {THEME.border};

    color: {THEME.text_secondary};
    font-family: var(--lg-mono-font);

    font-size: 0.59rem;
    line-height: 1.5;

    text-transform: uppercase;
    letter-spacing: 0.04em;
}}


.lg-state-panel {{
    padding: 1.35rem 1.45rem;

    background: {THEME.surface};
    border: 1px solid {THEME.border};
    border-radius: {THEME.radius_large};

    color: {THEME.text_secondary};

    font-size: 0.92rem;
    line-height: 1.65;
}}

.lg-state-panel strong {{
    color: {THEME.text_primary};
}}


@media (max-width: 900px) {{

    .lg-metric-grid {{
        grid-template-columns:
            repeat(3, minmax(0, 1fr));
    }}

    .lg-evidence-grid {{
        grid-template-columns: 1fr;
    }}

    .lg-control-context {{
        align-items: flex-start;
        text-align: left;
    }}
}}

@media (max-width: 560px) {{

    .lg-page-intro h1 {{
        font-size: 2rem;
    }}

    .lg-metric-grid {{
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }}

    .lg-finding-summary {{
        grid-template-columns: 1fr;
    }}

    .lg-masked-value {{
        text-align: left;
    }}
}}

</style>
"""


def inject_component_styles() -> None:
    """
    Inject LeakGuard component styling.
    """

    st.html(
        build_component_css()
    )


def render_brand_header(
    *,
    api_connected: bool,
    service_version: str | None = None,
) -> None:
    """
    Render the compact product header.
    """

    status_text = (
        "Local API connected"
        if api_connected
        else "Local API unavailable"
    )

    dot_class = (
        "lg-api-dot"
        if api_connected
        else (
            "lg-api-dot "
            "lg-api-dot-offline"
        )
    )

    version_text = ""

    if api_connected and service_version:
        version_text = (
            " · v"
            + escape_ui_text(
                service_version
            )
        )

    st.html(
        f"""
<div class="lg-brandbar">

    <div class="lg-brand-left">

        <img
            src="{logo_data_uri()}"
            alt="LeakGuard AI logo"
            style="
                width:43px;
                height:43px;
                flex:0 0 43px;
                display:block;
                object-fit:contain;
                border-radius:9px;
            "
        >

        <div>
            <div class="lg-brand-title">
                LeakGuard AI
            </div>

            <div class="lg-api-status">
                <span class="{dot_class}"></span>
                {escape_ui_text(status_text)}
                {version_text}
            </div>
        </div>

    </div>

    <div class="lg-product-chip">
        Security Gate
    </div>

</div>
"""
    )


def render_sidebar(
    *,
    api_connected: bool,
    scan_recently_run: bool = False,
) -> None:
    """
    Render the LeakGuard workspace sidebar.

    The scan item can briefly pulse after a
    completed scan.
    """

    status_color = (
        THEME.brand
        if api_connected
        else THEME.critical
    )

    status_text = (
        "Local API connected"
        if api_connected
        else "Local API unavailable"
    )

    if scan_recently_run:
        scan_background = THEME.brand
        scan_border = THEME.brand_dark
        scan_animation = (
            "animation:lgScanPulse "
            "780ms ease-out 2;"
        )
    else:
        scan_background = "#F7F9F5"
        scan_border = THEME.border
        scan_animation = ""

    st.sidebar.html(
        f"""
<style>

@keyframes lgScanPulse {{
    0% {{
        transform: scale(1);
        box-shadow:
            0 0 0 0
            rgba(119, 227, 79, 0.38);
    }}

    50% {{
        transform: scale(1.018);
        box-shadow:
            0 0 0 9px
            rgba(119, 227, 79, 0.10);
    }}

    100% {{
        transform: scale(1);
        box-shadow:
            0 0 0 0
            rgba(119, 227, 79, 0);
    }}
}}

</style>

<div style="
    min-height: calc(100vh - 18px);
    box-sizing: border-box;

    display: flex;
    flex-direction: column;

    margin-top: -18px;
    padding: 0 8px 16px;

    font-family:
        Inter,
        Segoe UI,
        sans-serif;
">

    <div style="
        display: flex;
        align-items: center;
        gap: 12px;

        margin-bottom: 24px;
    ">

        <img
            src="{logo_data_uri()}"
            alt="LeakGuard AI sidebar logo"
            style="
                width:44px;
                height:44px;
                flex:0 0 44px;
                display:block;
                object-fit:contain;
                border-radius:9px;
            "
        >

        <div style="min-width:0;">

            <div style="
                color: {THEME.text_primary};

                font-size: 20px;
                font-weight: 800;
                line-height: 22px;

                letter-spacing: -0.5px;
            ">
                LeakGuard AI
            </div>

            <div style="
                margin-top: 4px;

                color: {THEME.text_secondary};

                font-family:
                    Consolas,
                    monospace;

                font-size: 10px;
                line-height: 14px;
            ">
                Security Gate
            </div>

        </div>

    </div>


    <div style="
        margin: 0 8px 8px;

        color: {THEME.text_muted};

        font-family:
            Consolas,
            monospace;

        font-size: 9px;
        font-weight: 700;

        letter-spacing: 1.25px;
        text-transform: uppercase;
    ">
        Workspace
    </div>


    <div style="
        min-height: 45px;
        box-sizing: border-box;

        display: flex;
        align-items: center;
        gap: 10px;

        padding: 0 14px;

        background: {scan_background};
        border: 1px solid {scan_border};
        border-radius: 9px;

        color: #111827;

        font-size: 14px;
        font-weight: 700;

        {scan_animation}
    ">

        <span style="
            width: 7px;
            height: 7px;
            flex: 0 0 7px;

            border-radius: 999px;
            background: {THEME.brand_dark};
        "></span>

        <span>
            Security Scan
        </span>

    </div>


    <div style="
        height: 1px;
        margin: 23px 0;

        background: {THEME.border};
    "></div>


    <div style="
        padding: 13px 14px;

        background: #F5FAF2;
        border: 1px solid #DDEBD8;
        border-radius: 9px;
    ">

        <div style="
            display: flex;
            align-items: center;
            gap: 8px;
        ">

            <span style="
                width: 8px;
                height: 8px;
                flex: 0 0 8px;

                border-radius: 999px;
                background: {status_color};
            "></span>

            <span style="
                color: {THEME.text_primary};

                font-size: 13px;
                font-weight: 600;
            ">
                {status_text}
            </span>

        </div>

        <div style="
            margin: 6px 0 0 16px;

            color: {THEME.text_secondary};

            font-family:
                Consolas,
                monospace;

            font-size: 9px;
            line-height: 14px;
        ">
            Local processing boundary
        </div>

    </div>


    <div style="
        margin-top: 22px;
        padding: 0 8px;
    ">

        <div style="
            margin-bottom: 10px;

            color: {THEME.text_muted};

            font-family:
                Consolas,
                monospace;

            font-size: 9px;
            font-weight: 700;

            letter-spacing: 1.1px;
            text-transform: uppercase;
        ">
            Privacy
        </div>

        <div style="
            display: flex;
            gap: 9px;

            margin-bottom: 9px;

            color: {THEME.text_secondary};

            font-size: 11px;
            line-height: 16px;
        ">
            <span style="
                width: 5px;
                height: 5px;
                flex: 0 0 5px;

                margin-top: 5px;

                border-radius: 999px;
                background: {THEME.brand};
            "></span>

            <span>
                Masked public output
            </span>
        </div>

        <div style="
            display: flex;
            gap: 9px;

            color: {THEME.text_secondary};

            font-size: 11px;
            line-height: 16px;
        ">
            <span style="
                width: 5px;
                height: 5px;
                flex: 0 0 5px;

                margin-top: 5px;

                border-radius: 999px;
                background: {THEME.brand};
            "></span>

            <span>
                No external credential validation
            </span>
        </div>

    </div>


    <div style="
        margin-top: auto;
        padding: 18px 8px 0;

        color: {THEME.text_muted};

        font-family:
            Consolas,
            monospace;

        font-size: 9px;
    ">
        LeakGuard AI&nbsp;&nbsp;v0.1.0
    </div>

</div>
"""
    )


def render_page_intro() -> None:
    """
    Render the security scan page title.
    """

    st.html(
        """
<div class="lg-page-intro">
    <h1>Security Scan</h1>

    <p>
        Inspect source code, staged Git changes,
        and build artifacts before they ship.
    </p>
</div>
"""
    )


def render_scan_context() -> None:
    """
    Render local-first processing context.
    """

    st.html(
        """
<div class="lg-control-context">
    <span>Local processing</span>
    <span>No external credential validation</span>
</div>
"""
    )


def render_scan_form() -> ScanFormSubmission | None:
    """
    Render scan controls.
    """

    ml_labels = {
        ML_POLICY_CHOICES[0]:
            "Project config",
        ML_POLICY_CHOICES[1]:
            "Candidate v2 on",
        ML_POLICY_CHOICES[2]:
            "Off",
    }

    with st.form(
        "leakguard_scan_form",
        border=True,
    ):
        path_column, target_column = (
            st.columns(
                [3.3, 1.7],
                gap="medium",
            )
        )

        with path_column:
            project_path = st.text_input(
                "Scan path",
                value=".",
                help=(
                    "Path must remain inside "
                    "the FastAPI scan root."
                ),
            )

        with target_column:
            scan_target = st.segmented_control(
                "Scan target",
                options=(
                    "Project",
                    "Staged Git",
                ),
                default="Project",
                selection_mode="single",
                key="leakguard_scan_target",
                help=(
                    "Project scans the working "
                    "project. Staged Git scans "
                    "the Git index."
                ),
            )

        st.html(
            '<div class="lg-form-divider">'
            "</div>"
        )

        ml_column, context_column = (
            st.columns(
                [2.5, 1.5],
                gap="large",
            )
        )

        with ml_column:
            ml_policy = st.segmented_control(
                "ML advisory",
                options=ML_POLICY_CHOICES,
                default=ML_POLICY_CHOICES[0],
                selection_mode="single",
                format_func=(
                    lambda choice:
                    ml_labels[choice]
                ),
                key="leakguard_ml_policy",
                help=(
                    "Candidate v2 is "
                    "experimental and never "
                    "has independent blocking "
                    "authority."
                ),
            )

        with context_column:
            render_scan_context()

        submitted = st.form_submit_button(
            "Run security scan",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return None

    if scan_target is None:
        scan_target = "Project"

    if ml_policy is None:
        ml_policy = ML_POLICY_CHOICES[0]

    return ScanFormSubmission(
        project_path=project_path,
        staged=(
            scan_target == "Staged Git"
        ),
        ml_policy=ml_policy,
    )


def build_gate_markup(
    scan_view: ScanView,
) -> str:
    """
    Build validated security gate markup.
    """

    style = gate_style(
        scan_view.gate
    )

    gate_text = (
        "PASS"
        if scan_view.gate == "passed"
        else "FAIL"
    )

    if scan_view.gate == "passed":
        description = (
            "No blocking findings were "
            "reported for this scan."
        )
    else:
        suffix = (
            ""
            if scan_view.findings_count == 1
            else "s"
        )

        description = (
            f"{scan_view.findings_count} "
            f"finding{suffix} require review "
            "before this project is "
            "considered clear."
        )

    metrics = (
        (
            scan_view.files_scanned,
            "Files",
            THEME.text_primary,
        ),
        (
            scan_view.findings_count,
            "Findings",
            THEME.text_primary,
        ),
        (
            scan_view.severity.critical,
            "Critical",
            THEME.critical,
        ),
        (
            scan_view.severity.high,
            "High",
            THEME.high,
        ),
        (
            scan_view.severity.medium,
            "Medium",
            THEME.medium,
        ),
        (
            scan_view.severity.low,
            "Low",
            THEME.low,
        ),
    )

    metric_markup = "".join(
        f"""
<div class="lg-metric">
    <span
        class="lg-metric-value"
        style="color:{color};"
    >
        {value}
    </span>

    <span class="lg-metric-name">
        {name}
    </span>
</div>
"""
        for value, name, color
        in metrics
    )

    return f"""
<div class="lg-gate-card">

    <div
        class="lg-gate-accent"
        style="background:{style.accent};"
    ></div>

    <div class="lg-gate-label">
        Security Gate
    </div>

    <div
        class="lg-gate-state"
        style="color:{style.text};"
    >
        {gate_text}
    </div>

    <div class="lg-gate-copy">
        {escape_ui_text(description)}
    </div>

    <div class="lg-metric-grid">
        {metric_markup}
    </div>

</div>
"""


def render_gate_summary(
    scan_view: ScanView,
) -> None:
    """
    Render PASS / FAIL and aggregate metrics.
    """

    st.html(
        build_gate_markup(
            scan_view
        )
    )

    mode_text = (
        "Staged Git index"
        if scan_view.mode == "staged"
        else "Working project"
    )

    ml_text = (
        "Candidate v2 enabled · advisory only"
        if scan_view.ml_advisory_enabled
        else "Candidate v2 disabled"
    )

    st.caption(
        f"Scan mode: {mode_text} · "
        f"{ml_text}"
    )


def build_advisory_markup(
    finding: FindingView,
) -> str:
    """
    Build optional Candidate v2 presentation.
    """

    advisory = finding.ml_advisory

    if advisory is None:
        return ""

    prediction = (
        "Suspicious context"
        if advisory.prediction
        == "suspicious"
        else "Lower-risk context"
    )

    return f"""
<div class="lg-advisory-panel">

    <div class="lg-advisory-title">

        <span class="lg-advisory-name">
            ML Advisory
        </span>

        <span class="lg-advisory-chip">
            {escape_ui_text(advisory.model)}
        </span>

    </div>

    <div class="lg-fact-row">
        <span class="lg-fact-name">
            Risk score
        </span>

        <span class="lg-fact-value">
            {advisory.risk_score:.3f}
        </span>
    </div>

    <div class="lg-fact-row">
        <span class="lg-fact-name">
            Prediction
        </span>

        <span class="lg-fact-value">
            {escape_ui_text(prediction)}
        </span>
    </div>

    <div class="lg-fact-row">
        <span class="lg-fact-name">
            Threshold
        </span>

        <span class="lg-fact-value">
            {advisory.threshold:.3f}
        </span>
    </div>

    <div class="lg-advisory-footer">
        Advisory only · Non-blocking ·
        Not a calibrated probability
    </div>

</div>
"""


def build_finding_detail_markup(
    finding: FindingView,
) -> str:
    """
    Build one escaped finding detail view.
    """

    style = severity_style(
        finding.severity
    )

    if finding.reasons:
        reason_markup = "".join(
            (
                "<li>"
                + escape_ui_text(reason)
                + "</li>"
            )
            for reason in finding.reasons
        )
    else:
        reason_markup = (
            "<li>No additional reason "
            "metadata was reported.</li>"
        )

    candidate_markup = ""

    if finding.candidate_score is not None:
        candidate_markup = f"""
<div class="lg-fact-row">
    <span class="lg-fact-name">
        Candidate score
    </span>

    <span class="lg-fact-value">
        {finding.candidate_score} / 100
    </span>
</div>
"""

    framework_markup = ""

    if finding.framework is not None:
        framework_markup = f"""
<div class="lg-fact-row">
    <span class="lg-fact-name">
        Framework
    </span>

    <span class="lg-fact-value">
        {escape_ui_text(finding.framework)}
    </span>
</div>
"""

    advisory_markup = (
        build_advisory_markup(
            finding
        )
    )

    if advisory_markup:
        right_panel = advisory_markup
    else:
        right_panel = f"""
<div class="lg-evidence-panel">

    <span class="lg-section-label">
        Finding metadata
    </span>

    <div class="lg-fact-row">
        <span class="lg-fact-name">
            Severity
        </span>

        <span class="lg-fact-value">
            {escape_ui_text(finding.severity)}
        </span>
    </div>

    {candidate_markup}
    {framework_markup}

</div>
"""

    return f"""
<div class="lg-finding-detail">

    <div class="lg-finding-summary">

        <div>

            <span
                class="lg-severity"
                style="
                    color:{style.text};
                    background:{style.background};
                    border:
                        1px solid
                        {style.accent}33;
                "
            >
                {escape_ui_text(finding.severity)}
            </span>

            <div class="lg-finding-type">
                {escape_ui_text(
                    finding.finding_type
                )}
            </div>

            <div class="lg-finding-location">
                {escape_ui_text(finding.file)}
                · Line {finding.line}
            </div>

        </div>

        <div class="lg-masked-value">
            {escape_ui_text(
                finding.masked_value
            )}
        </div>

    </div>

    <div class="lg-evidence-grid">

        <div class="lg-evidence-panel">

            <span class="lg-section-label">
                Why LeakGuard flagged this
            </span>

            <ul class="lg-reason-list">
                {reason_markup}
            </ul>

            <div style="margin-top:0.9rem;">

                <div class="lg-fact-row">
                    <span class="lg-fact-name">
                        Source
                    </span>

                    <span class="lg-fact-value">
                        {escape_ui_text(
                            finding.file
                        )}
                        : {finding.line}
                    </span>
                </div>

                <div class="lg-fact-row">
                    <span class="lg-fact-name">
                        Masked value
                    </span>

                    <span class="lg-fact-value">
                        {escape_ui_text(
                            finding.masked_value
                        )}
                    </span>
                </div>

                {candidate_markup}
                {framework_markup}

            </div>

        </div>

        {right_panel}

    </div>

</div>
"""


def render_findings(
    scan_view: ScanView,
) -> None:
    """
    Render validated findings.
    """

    if not scan_view.findings:
        st.html(
            """
<div class="lg-state-panel">
    <strong>
        No blocking findings detected.
    </strong>
    The current scan returned a clear
    security gate result.
</div>
"""
        )

        return

    st.html(
        f"""
<div class="lg-findings-header">

    <h2>Findings</h2>

    <span>
        {scan_view.findings_count}
        requiring review · masked output only
    </span>

</div>
"""
    )

    for index, finding in enumerate(
        scan_view.findings,
        start=1,
    ):
        label = (
            f"{finding.severity} · "
            f"{finding.finding_type} · "
            f"{finding.file}:{finding.line}"
        )

        with st.expander(
            label,
            expanded=(index == 1),
        ):
            st.html(
                build_finding_detail_markup(
                    finding
                )
            )


def render_api_unavailable() -> None:
    """
    Render local API unavailable state.
    """

    st.html(
        """
<div class="lg-state-panel">
    <strong>Local API unavailable.</strong>
    Start the LeakGuard API service before
    running a security scan. Scan controls
    remain unavailable until the local
    security boundary is healthy.
</div>
"""
    )