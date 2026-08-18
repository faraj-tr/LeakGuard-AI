from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class LeakGuardTheme:
    """
    Visual design tokens for the LeakGuard AI
    dashboard.

    The identity follows the approved
    "Calm Forensic Intelligence" direction.
    """

    # Core surfaces
    background: str = "#F7F8F4"
    surface: str = "#FFFFFF"
    surface_subtle: str = "#F9FAFB"

    # Typography
    text_primary: str = "#131C26"
    text_secondary: str = "#4B5563"
    text_muted: str = "#6B7280"

    # Structure
    border: str = "#E5E7EB"
    border_strong: str = "#D1D5DB"

    # LeakGuard brand
    brand: str = "#77E34F"
    brand_dark: str = "#206D00"
    brand_deep: str = "#1C6300"
    brand_soft: str = "#EFFBEA"

    # Semantic security states
    critical: str = "#DC2626"
    critical_soft: str = "#FEF2F2"
    critical_text: str = "#B91C1C"

    high: str = "#D97706"
    high_soft: str = "#FFFBEB"
    high_text: str = "#B45309"

    medium: str = "#6B7280"
    medium_soft: str = "#F3F4F6"
    medium_text: str = "#4B5563"

    low: str = "#2563EB"
    low_soft: str = "#EFF6FF"
    low_text: str = "#1D4ED8"

    # Informational/advisory surfaces
    advisory: str = "#52734D"
    advisory_soft: str = "#F2F7F0"

    # Shape
    radius_small: str = "4px"
    radius: str = "8px"
    radius_large: str = "12px"

    # Elevation
    shadow_interactive: str = (
        "0 4px 12px rgba(0, 0, 0, 0.03)"
    )


@dataclass(frozen=True)
class SeverityStyle:
    """
    Presentation tokens for one finding
    severity.
    """

    accent: str
    background: str
    text: str


@dataclass(frozen=True)
class GateStyle:
    """
    Presentation tokens for one security gate
    state.
    """

    accent: str
    background: str
    text: str


THEME: Final = LeakGuardTheme()


HEADING_FONT_STACK: Final[str] = (
    '"Sora", '
    '"Segoe UI Variable Display", '
    '"Aptos Display", '
    '"Segoe UI", '
    "sans-serif"
)

BODY_FONT_STACK: Final[str] = (
    '"Inter", '
    '"Segoe UI Variable Text", '
    '"Aptos", '
    '"Segoe UI", '
    "sans-serif"
)

MONO_FONT_STACK: Final[str] = (
    '"JetBrains Mono", '
    '"Cascadia Code", '
    '"Cascadia Mono", '
    '"Consolas", '
    "monospace"
)


SEVERITY_STYLES: Final[
    dict[str, SeverityStyle]
] = {
    "CRITICAL": SeverityStyle(
        accent=THEME.critical,
        background=THEME.critical_soft,
        text=THEME.critical_text,
    ),
    "HIGH": SeverityStyle(
        accent=THEME.high,
        background=THEME.high_soft,
        text=THEME.high_text,
    ),
    "MEDIUM": SeverityStyle(
        accent=THEME.medium,
        background=THEME.medium_soft,
        text=THEME.medium_text,
    ),
    "LOW": SeverityStyle(
        accent=THEME.low,
        background=THEME.low_soft,
        text=THEME.low_text,
    ),
}


GATE_STYLES: Final[
    dict[str, GateStyle]
] = {
    "passed": GateStyle(
        accent=THEME.brand_dark,
        background=THEME.brand_soft,
        text=THEME.brand_deep,
    ),
    "failed": GateStyle(
        accent=THEME.critical,
        background=THEME.critical_soft,
        text=THEME.critical_text,
    ),
}


def severity_style(
    severity: str,
) -> SeverityStyle:
    """
    Resolve a normalized finding severity.

    Unknown severities receive the neutral
    MEDIUM presentation instead of creating
    an unsafe visual assumption.
    """

    normalized = severity.strip().upper()

    return SEVERITY_STYLES.get(
        normalized,
        SEVERITY_STYLES["MEDIUM"],
    )


def gate_style(
    gate: str,
) -> GateStyle:
    """
    Resolve a normalized gate presentation.

    Unknown states use the failed visual state
    so presentation does not imply success.
    """

    normalized = gate.strip().lower()

    return GATE_STYLES.get(
        normalized,
        GATE_STYLES["failed"],
    )