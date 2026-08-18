import streamlit as st

from leakguard.ui.theme import gate_style


PASS_ACCENT = gate_style(
    "passed"
).accent

FAIL_ACCENT = gate_style(
    "failed"
).accent


RESULTS_PREVIEW_CSS = f"""
<style>

/*
 * LeakGuard Results Preview
 *
 * Centered PASS / FAIL presentation with
 * one-time, status-aware entrance feedback.
 *
 * No scanner, API, workflow, sidebar,
 * finding, or gate logic is changed.
 */


/* ==========================================================
   Gate shell
   ========================================================== */

.lg-gate-card {{
    position: relative;

    overflow: hidden;

    margin-top: 2rem;

    padding:
        2.4rem 2.25rem 2.1rem;

    background:
        #FFFFFF;

    border:
        1px solid #E1E5E0;

    border-radius:
        11px;

    text-align:
        center;

    box-shadow:
        0 1px 2px
        rgba(19, 28, 38, 0.025);

    transform-origin:
        center center;

    will-change:
        transform,
        opacity,
        box-shadow;
}}


.lg-gate-accent {{
    height:
        4px;
}}


/* ==========================================================
   FAIL entrance
   ========================================================== */

.lg-gate-card:has(
    .lg-gate-accent[
        style*="background:{FAIL_ACCENT}"
    ]
) {{
    animation:
        lgGateFailIntro
        950ms
        cubic-bezier(
            0.22,
            1,
            0.36,
            1
        )
        both;
}}


@keyframes lgGateFailIntro {{

    0% {{
        opacity:
            0;

        transform:
            translateY(8px)
            scale(0.988);

        box-shadow:
            0 0 0 0
            rgba(220, 38, 38, 0);
    }}

    42% {{
        opacity:
            1;

        transform:
            translateY(0)
            scale(1.008);

        box-shadow:
            0 0 0 8px
            rgba(220, 38, 38, 0.075);
    }}

    72% {{
        transform:
            scale(0.998);

        box-shadow:
            0 0 0 4px
            rgba(220, 38, 38, 0.035);
    }}

    100% {{
        opacity:
            1;

        transform:
            translateY(0)
            scale(1);

        box-shadow:
            0 1px 2px
            rgba(19, 28, 38, 0.025);
    }}
}}


/* ==========================================================
   PASS entrance
   ========================================================== */

.lg-gate-card:has(
    .lg-gate-accent[
        style*="background:{PASS_ACCENT}"
    ]
) {{
    animation:
        lgGatePassIntro
        950ms
        cubic-bezier(
            0.22,
            1,
            0.36,
            1
        )
        both;
}}


@keyframes lgGatePassIntro {{

    0% {{
        opacity:
            0;

        transform:
            translateY(8px)
            scale(0.988);

        box-shadow:
            0 0 0 0
            rgba(119, 227, 79, 0);
    }}

    42% {{
        opacity:
            1;

        transform:
            translateY(0)
            scale(1.008);

        box-shadow:
            0 0 0 8px
            rgba(119, 227, 79, 0.10);
    }}

    72% {{
        transform:
            scale(0.998);

        box-shadow:
            0 0 0 4px
            rgba(119, 227, 79, 0.045);
    }}

    100% {{
        opacity:
            1;

        transform:
            translateY(0)
            scale(1);

        box-shadow:
            0 1px 2px
            rgba(19, 28, 38, 0.025);
    }}
}}


/* ==========================================================
   Centered security gate content
   ========================================================== */

.lg-gate-label {{
    margin:
        0 auto 1rem;

    color:
        #5D6B82;

    font-size:
        0.64rem;

    font-weight:
        800;

    text-align:
        center;

    text-transform:
        uppercase;

    letter-spacing:
        0.18em;
}}


.lg-gate-state {{
    margin:
        0 auto;

    font-size:
        clamp(
            4.6rem,
            8vw,
            6.3rem
        );

    font-weight:
        800;

    line-height:
        0.9;

    text-align:
        center;

    letter-spacing:
        -0.065em;
}}


.lg-gate-copy {{
    max-width:
        48rem;

    margin:
        1.15rem auto 0;

    color:
        #4B5563;

    font-size:
        0.97rem;

    line-height:
        1.65;

    text-align:
        center;
}}


/* ==========================================================
   Metrics
   ========================================================== */

.lg-metric-grid {{
    width:
        100%;

    max-width:
        none;

    margin:
        2.25rem auto 0;

    display:
        grid;

    grid-template-columns:
        repeat(
            6,
            minmax(0, 1fr)
        );

    gap:
        0;

    overflow:
        hidden;

    background:
        #FFFFFF;

    border:
        1px solid #E1E5E0;

    border-radius:
        9px;
}}


.lg-metric {{
    min-width:
        0;

    min-height:
        5.4rem;

    box-sizing:
        border-box;

    display:
        flex;

    flex-direction:
        column;

    align-items:
        center;

    justify-content:
        center;

    padding:
        0.9rem 0.8rem;

    border-right:
        1px solid #E1E5E0;

    text-align:
        center;
}}


.lg-metric:last-child {{
    border-right:
        0;
}}


.lg-metric-value {{
    display:
        block;

    font-size:
        1.7rem;

    font-weight:
        750;

    line-height:
        1;

    text-align:
        center;
}}


.lg-metric-name {{
    display:
        block;

    margin-top:
        0.5rem;

    color:
        #6B7280;

    font-size:
        0.54rem;

    font-weight:
        800;

    text-align:
        center;

    letter-spacing:
        0.085em;
}}


/* ==========================================================
   Reduced motion accessibility
   ========================================================== */

@media (
    prefers-reduced-motion:
    reduce
) {{

    .lg-gate-card {{
        animation:
            none !important;

        transform:
            none !important;
    }}
}}


/* ==========================================================
   Responsive
   ========================================================== */

@media (
    max-width: 900px
) {{

    .lg-gate-card {{
        padding:
            1.9rem
            1.35rem
            1.5rem;
    }}

    .lg-gate-state {{
        font-size:
            clamp(
                3.8rem,
                15vw,
                5rem
            );
    }}

    .lg-metric-grid {{
        grid-template-columns:
            repeat(
                3,
                minmax(0, 1fr)
            );
    }}

    .lg-metric:nth-child(3) {{
        border-right:
            0;
    }}
}}


@media (
    max-width: 560px
) {{

    .lg-metric-grid {{
        grid-template-columns:
            repeat(
                2,
                minmax(0, 1fr)
            );
    }}

    .lg-metric:nth-child(3) {{
        border-right:
            1px solid #E1E5E0;
    }}

    .lg-metric:nth-child(even) {{
        border-right:
            0;
    }}

    .lg-gate-copy {{
        font-size:
            0.9rem;
    }}
}}

</style>
"""


def inject_results_preview() -> None:
    """
    Inject the experimental centered
    PASS / FAIL presentation layer.
    """

    st.html(
        RESULTS_PREVIEW_CSS
    )