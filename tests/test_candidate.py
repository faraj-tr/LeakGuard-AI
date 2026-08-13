from leakguard.candidate import analyze_candidate


def test_random_like_unknown_value_is_suspicious():
    result = analyze_candidate(
        variable_name="x",
        value="K7mP2xQ9vL4sN8zA1c",
    )

    assert result["is_suspicious"] is True
    assert result["score"] >= 50
    assert "High entropy" in result["reasons"]


def test_simple_ui_text_is_not_suspicious():
    result = analyze_candidate(
        variable_name="message",
        value="Please enter your password",
    )

    assert result["is_suspicious"] is False


def test_sensitive_variable_increases_score():
    result = analyze_candidate(
        variable_name="api_key",
        value="LEAKGUARD_FAKE_KEY_ABC123",
    )

    assert result["score"] >= 40
    assert "Sensitive variable name" in result["reasons"]


def test_repeated_value_is_not_random_candidate():
    result = analyze_candidate(
        variable_name="value",
        value="aaaaaaaaaaaaaaaaaaaa",
    )

    assert result["is_suspicious"] is False
    assert result["entropy"] == 0.0