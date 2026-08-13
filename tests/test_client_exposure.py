from leakguard.client_exposure import (
    analyze_client_exposure,
    detect_client_framework,
)


def test_detects_vite_client_variable():
    framework = detect_client_framework(
        "VITE_API_KEY"
    )

    assert framework == "Vite"


def test_detects_nextjs_public_variable():
    framework = detect_client_framework(
        "NEXT_PUBLIC_API_KEY"
    )

    assert framework == "Next.js"


def test_vite_sensitive_variable_is_critical():
    result = analyze_client_exposure(
        variable_name="VITE_OPENAI_API_KEY",
        value="LEAKGUARD_FAKE_KEY_ABC123",
    )

    assert result["is_client_exposed"] is True
    assert result["is_risky"] is True
    assert result["framework"] == "Vite"
    assert result["severity"] == "CRITICAL"


def test_public_ui_variable_is_not_secret():
    result = analyze_client_exposure(
        variable_name="VITE_APP_TITLE",
        value="LeakGuard",
    )

    assert result["is_client_exposed"] is True
    assert result["is_risky"] is False
    assert result["severity"] is None