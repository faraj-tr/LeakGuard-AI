from pathlib import Path

import pandas as pd
import pytest

from leakguard.ml.advisory import (
    fit_candidate_v2_advisory_runtime,
)
from leakguard.ml.candidate_v2_locked import (
    LOCKED_THRESHOLD,
    build_locked_candidate_v2_decisions,
)
from leakguard.ml.dataset_v3 import (
    generate_synthetic_dataset_v3,
)
from leakguard.scanner import (
    scan_content,
)


TEST_SECRET = (
    "K7mP2xQ9vL4sN8zA1c"
)


@pytest.fixture(
    scope="module"
)
def training_dataframe():
    return (
        generate_synthetic_dataset_v3(
            samples_per_class=180,
            seed=1337,
        )
    )


@pytest.fixture(
    scope="module"
)
def advisory_runtime(
    training_dataframe,
):
    return (
        fit_candidate_v2_advisory_runtime(
            training_dataframe
        )
    )


def test_advisory_runtime_contract_does_not_expose_raw_value(
    advisory_runtime,
):
    variable_name = "opaque_value"

    result = advisory_runtime.score(
        variable_name=variable_name,
        value=TEST_SECRET,
    )

    assert result[
        "available"
    ] is True

    assert result[
        "model"
    ] == "candidate-v2"

    assert result[
        "mode"
    ] == "advisory"

    assert result[
        "blocking"
    ] is False

    assert result[
        "calibrated"
    ] is False

    assert (
        0.0
        <= result[
            "risk_score"
        ]
        <= 1.0
    )

    assert result[
        "threshold"
    ] == LOCKED_THRESHOLD

    assert result[
        "prediction"
    ] in {
        "suspicious",
        "lower_risk",
    }

    assert TEST_SECRET not in str(
        result
    )

    assert variable_name not in str(
        result
    )


def test_runtime_score_matches_locked_candidate_v2(
    training_dataframe,
    advisory_runtime,
):
    evaluation = pd.DataFrame(
        [
            {
                "variable_name": (
                    "opaque_value"
                ),
                "value": TEST_SECRET,
                "label": 1,
            }
        ]
    )

    locked = (
        build_locked_candidate_v2_decisions(
            training_dataframe=(
                training_dataframe
            ),
            evaluation_dataframe=(
                evaluation
            ),
        )
    )

    runtime_result = (
        advisory_runtime.score(
            variable_name=(
                "opaque_value"
            ),
            value=TEST_SECRET,
        )
    )

    assert runtime_result[
        "risk_score"
    ] == pytest.approx(
        float(
            locked.iloc[
                0
            ][
                "fusion_probability"
            ]
        )
    )


class StubAdvisoryRuntime:

    def __init__(
        self,
        risk_score=0.10,
    ):
        self.risk_score = (
            risk_score
        )

        self.calls = []

    def score(
        self,
        variable_name,
        value,
    ):
        self.calls.append(
            (
                variable_name,
                value,
            )
        )

        return {
            "available": True,
            "model": "candidate-v2",
            "mode": "advisory",
            "risk_score": (
                self.risk_score
            ),
            "threshold": 0.50,
            "prediction": (
                "suspicious"
                if self.risk_score
                >= 0.50
                else "lower_risk"
            ),
            "calibrated": False,
            "blocking": False,
        }


def test_generic_finding_receives_ml_advisory_without_suppression():
    runtime = StubAdvisoryRuntime(
        risk_score=0.05
    )

    findings = scan_content(
        path=Path(
            "mystery.py"
        ),
        content=(
            f'x = "{TEST_SECRET}"'
        ),
        ml_advisory_runtime=runtime,
    )

    assert len(
        findings
    ) == 1

    finding = findings[0]

    assert finding[
        "type"
    ] == (
        "Unknown Secret Candidate"
    )

    assert finding[
        "severity"
    ] == "MEDIUM"

    assert finding[
        "ml_advisory"
    ][
        "risk_score"
    ] == 0.05

    assert finding[
        "ml_advisory"
    ][
        "blocking"
    ] is False

    assert len(
        runtime.calls
    ) == 1

    assert TEST_SECRET not in str(
        findings
    )


def test_scanner_without_runtime_preserves_original_finding_shape():
    findings = scan_content(
        path=Path(
            "mystery.py"
        ),
        content=(
            f'x = "{TEST_SECRET}"'
        ),
    )

    assert len(
        findings
    ) == 1

    assert (
        "ml_advisory"
        not in findings[0]
    )


def test_known_pattern_is_not_sent_to_advisory_model():
    runtime = StubAdvisoryRuntime(
        risk_score=0.99
    )

    secret = (
        "LEAKGUARD_FAKE_PASSWORD_123"
    )

    findings = scan_content(
        path=Path(
            "config.py"
        ),
        content=(
            f'DB_PASSWORD = "{secret}"'
        ),
        ml_advisory_runtime=runtime,
    )

    assert len(
        findings
    ) == 1

    assert findings[
        0
    ][
        "type"
    ] == "Hardcoded Password"

    assert runtime.calls == []

    assert (
        "ml_advisory"
        not in findings[0]
    )


def test_ml_cannot_create_finding_for_safe_candidate():
    runtime = StubAdvisoryRuntime(
        risk_score=0.99
    )

    findings = scan_content(
        path=Path(
            "app.py"
        ),
        content=(
            'message = "Hello world"'
        ),
        ml_advisory_runtime=runtime,
    )

    assert findings == []

    assert runtime.calls == []
