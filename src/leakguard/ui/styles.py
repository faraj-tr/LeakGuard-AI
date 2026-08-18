import html

import streamlit as st

from leakguard.ui.theme import (
    BODY_FONT_STACK,
    HEADING_FONT_STACK,
    MONO_FONT_STACK,
    THEME,
)


def build_global_css() -> str:
    """
    Build the global LeakGuard dashboard CSS.

    The stylesheet intentionally relies on
    local/system font fallbacks and does not
    load remote design assets.
    """

    return f"""
<style>
:root {{
    --lg-background: {THEME.background};
    --lg-surface: {THEME.surface};
    --lg-surface-subtle: {THEME.surface_subtle};

    --lg-text: {THEME.text_primary};
    --lg-text-secondary: {THEME.text_secondary};
    --lg-text-muted: {THEME.text_muted};

    --lg-border: {THEME.border};
    --lg-border-strong: {THEME.border_strong};

    --lg-brand: {THEME.brand};
    --lg-brand-dark: {THEME.brand_dark};
    --lg-brand-deep: {THEME.brand_deep};
    --lg-brand-soft: {THEME.brand_soft};

    --lg-critical: {THEME.critical};
    --lg-critical-soft: {THEME.critical_soft};

    --lg-high: {THEME.high};
    --lg-high-soft: {THEME.high_soft};

    --lg-medium: {THEME.medium};
    --lg-medium-soft: {THEME.medium_soft};

    --lg-low: {THEME.low};
    --lg-low-soft: {THEME.low_soft};

    --lg-advisory: {THEME.advisory};
    --lg-advisory-soft: {THEME.advisory_soft};

    --lg-radius-sm: {THEME.radius_small};
    --lg-radius: {THEME.radius};
    --lg-radius-lg: {THEME.radius_large};

    --lg-shadow-interactive:
        {THEME.shadow_interactive};

    --lg-heading-font:
        {HEADING_FONT_STACK};

    --lg-body-font:
        {BODY_FONT_STACK};

    --lg-mono-font:
        {MONO_FONT_STACK};
}}


/* ========================================
   Streamlit chrome
   ======================================== */

[data-testid="stHeader"] {{
    display: none;
}}

[data-testid="stToolbar"] {{
    display: none;
}}

[data-testid="stDecoration"] {{
    display: none;
}}


/* ========================================
   Application canvas
   ======================================== */

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {{
    background:
        var(--lg-background);
    color:
        var(--lg-text);
    font-family:
        var(--lg-body-font);
}}

[data-testid="stAppViewContainer"] {{
    background:
        var(--lg-background);
}}

[data-testid="stMain"] {{
    background:
        var(--lg-background);
}}

.block-container {{
    max-width: 1280px;
    padding-top: 2.25rem;
    padding-bottom: 4rem;
    padding-left: 2rem;
    padding-right: 2rem;
}}


/* ========================================
   Typography
   ======================================== */

h1,
h2,
h3,
h4,
h5,
h6 {{
    font-family:
        var(--lg-heading-font) !important;
    color:
        var(--lg-text);
    letter-spacing:
        -0.025em;
}}

h1 {{
    font-weight: 650 !important;
}}

h2,
h3 {{
    font-weight: 600 !important;
}}

p,
li,
label,
[data-testid="stMarkdownContainer"] {{
    font-family:
        var(--lg-body-font);
}}

code,
pre,
kbd {{
    font-family:
        var(--lg-mono-font) !important;
}}


/* ========================================
   Sidebar
   ======================================== */

[data-testid="stSidebar"] {{
    background:
        var(--lg-surface);
    border-right:
        1px solid var(--lg-border);
}}

[data-testid="stSidebar"] > div {{
    background:
        var(--lg-surface);
}}

[data-testid="stSidebar"] hr {{
    border-color:
        var(--lg-border);
}}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {{
    color:
        var(--lg-text);
}}


/* ========================================
   Inputs
   ======================================== */

[data-testid="stTextInput"] input {{
    background:
        var(--lg-surface);
    color:
        var(--lg-text);
    border:
        1px solid var(--lg-border);
    border-radius:
        var(--lg-radius);
    box-shadow:
        none;
    font-family:
        var(--lg-mono-font);
}}

[data-testid="stTextInput"] input:hover {{
    border-color:
        var(--lg-border-strong);
}}

[data-testid="stTextInput"] input:focus {{
    border-color:
        var(--lg-brand) !important;
    box-shadow:
        0 0 0 2px
        rgba(119, 227, 79, 0.12) !important;
}}

[data-testid="stSelectbox"] > div > div {{
    border-radius:
        var(--lg-radius);
}}

[data-testid="stCheckbox"] label,
[data-testid="stRadio"] label {{
    color:
        var(--lg-text);
}}


/* ========================================
   Buttons
   ======================================== */

.stButton > button,
.stFormSubmitButton > button {{
    min-height:
        2.55rem;
    border-radius:
        var(--lg-radius);
    border:
        1px solid var(--lg-border);
    box-shadow:
        none;
    font-family:
        var(--lg-body-font);
    font-weight:
        600;
    transition:
        transform 120ms ease,
        border-color 120ms ease,
        background 120ms ease,
        box-shadow 120ms ease;
}}

.stButton > button:hover,
.stFormSubmitButton > button:hover {{
    border-color:
        var(--lg-brand-dark);
    box-shadow:
        var(--lg-shadow-interactive);
}}

.stButton > button:focus-visible,
.stFormSubmitButton > button:focus-visible {{
    outline:
        3px solid rgba(119, 227, 79, 0.28);
    outline-offset:
        2px;
}}

.stButton > button:active,
.stFormSubmitButton > button:active {{
    transform:
        translateY(1px);
}}

.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {{
    background:
        var(--lg-brand);
    color:
        #111827;
    border-color:
        var(--lg-brand);
}}

.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {{
    background:
        #6ED747;
    color:
        #111827;
}}


[data-testid="stFormSubmitButton"] button {{
    background: var(--lg-brand) !important;
    color: #111827 !important;
    border-color: var(--lg-brand) !important;
    font-weight: 600 !important;
}}

[data-testid="stFormSubmitButton"] button:hover {{
    background: #6ED747 !important;
    color: #111827 !important;
    border-color: var(--lg-brand-dark) !important;
}}


/* ========================================
   Forms and native Streamlit containers
   ======================================== */

[data-testid="stForm"] {{
    background:
        var(--lg-surface);
    border:
        1px solid var(--lg-border);
    border-radius:
        var(--lg-radius-lg);
    padding:
        1.25rem;
    box-shadow:
        none;
}}

[data-testid="stExpander"] {{
    background:
        var(--lg-surface);
    border:
        1px solid var(--lg-border);
    border-radius:
        var(--lg-radius);
    box-shadow:
        none;
    overflow:
        hidden;
}}

[data-testid="stExpander"]:hover {{
    border-color:
        var(--lg-border-strong);
}}

[data-testid="stMetric"] {{
    background:
        transparent;
}}

[data-testid="stMetricValue"] {{
    font-family:
        var(--lg-heading-font);
    font-weight:
        600;
    color:
        var(--lg-text);
}}

[data-testid="stMetricLabel"] {{
    color:
        var(--lg-text-secondary);
    font-family:
        var(--lg-mono-font);
    text-transform:
        uppercase;
    letter-spacing:
        0.06em;
    font-size:
        0.72rem;
}}


/* ========================================
   Alerts
   ======================================== */

[data-testid="stAlert"] {{
    border-radius:
        var(--lg-radius);
    border-width:
        1px;
    box-shadow:
        none;
}}


/* ========================================
   Dividers
   ======================================== */

hr {{
    border:
        none;
    border-top:
        1px solid var(--lg-border);
    margin:
        1.6rem 0;
}}


/* ========================================
   LeakGuard utility classes
   ======================================== */

.lg-app-shell {{
    width:
        100%;
}}

.lg-eyebrow {{
    display:
        inline-flex;
    align-items:
        center;
    gap:
        0.4rem;

    font-family:
        var(--lg-mono-font);
    font-size:
        0.68rem;
    font-weight:
        600;
    line-height:
        1;

    text-transform:
        uppercase;
    letter-spacing:
        0.09em;

    color:
        var(--lg-text-secondary);
}}

.lg-status-dot {{
    width:
        0.48rem;
    height:
        0.48rem;

    display:
        inline-block;

    border-radius:
        999px;

    background:
        var(--lg-brand);
}}

.lg-card {{
    background:
        var(--lg-surface);

    border:
        1px solid var(--lg-border);

    border-radius:
        var(--lg-radius-lg);

    box-shadow:
        none;
}}

.lg-card-interactive:hover {{
    border-color:
        var(--lg-border-strong);

    box-shadow:
        var(--lg-shadow-interactive);
}}

.lg-mono {{
    font-family:
        var(--lg-mono-font);
}}

.lg-muted {{
    color:
        var(--lg-text-secondary);
}}

.lg-security-note {{
    color:
        var(--lg-text-secondary);

    font-size:
        0.82rem;

    line-height:
        1.5;
}}

.lg-security-note strong {{
    color:
        var(--lg-text);
}}


/* ========================================
   Responsive behavior
   ======================================== */

@media
(max-width: 900px) {{

    .block-container {{
        padding-top:
            1.5rem;

        padding-left:
            1rem;

        padding-right:
            1rem;
    }}

    h1 {{
        font-size:
            2rem !important;
    }}
}}
</style>
"""


def inject_global_styles() -> None:
    """
    Inject the approved LeakGuard visual
    foundation into the Streamlit page.
    """

    st.html(build_global_css())


def escape_ui_text(
    value: object,
) -> str:
    """
    HTML-escape data before it is inserted
    into custom dashboard markup.

    Scanner/API-derived values must never be
    interpolated into unsafe HTML directly.
    """

    return html.escape(
        str(value),
        quote=True,
    )