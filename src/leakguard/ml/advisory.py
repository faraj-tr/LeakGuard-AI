from dataclasses import dataclass

import pandas as pd
from sklearn.pipeline import Pipeline

from leakguard.ml.candidate_v2_complementarity import (
    build_text_input,
    fit_text_probe,
)
from leakguard.ml.candidate_v2_locked import (
    LOCKED_CONTEXT_WEIGHT,
    LOCKED_TEXT_WEIGHT,
    LOCKED_THRESHOLD,
    validate_locked_configuration,
)
from leakguard.ml.context_baseline import (
    build_context_feature_frame,
    fit_context_model,
)


MODEL_NAME = "candidate-v2"
MODEL_MODE = "advisory"


@dataclass
class CandidateV2AdvisoryRuntime:
    """
    Runtime representation of the locked
    Candidate v2 models.

    The models are fitted once and reused
    for every candidate scored during a scan.

    Raw candidate values are never returned
    by this interface.
    """

    context_model: Pipeline
    text_model: Pipeline

    def score(
        self,
        variable_name: str,
        value: str,
    ) -> dict:
        """
        Score one candidate using the locked
        Candidate v2 late-fusion policy.

        The returned result is advisory only.
        It must never become blocking authority
        by itself.
        """

        validate_locked_configuration()

        evaluation = pd.DataFrame(
            [
                {
                    "variable_name": str(
                        variable_name
                    ),
                    "value": str(
                        value
                    ),
                    "label": 0,
                }
            ]
        )

        context_features = (
            build_context_feature_frame(
                evaluation
            )
        )

        text_input = build_text_input(
            evaluation
        )

        context_probability = float(
            self.context_model.predict_proba(
                context_features
            )[0, 1]
        )

        text_probability = float(
            self.text_model.predict_proba(
                text_input
            )[0, 1]
        )

        fusion_probability = float(
            LOCKED_TEXT_WEIGHT
            * text_probability
            + LOCKED_CONTEXT_WEIGHT
            * context_probability
        )

        suspicious = (
            fusion_probability
            >= LOCKED_THRESHOLD
        )

        return {
            "available": True,
            "model": MODEL_NAME,
            "mode": MODEL_MODE,
            "risk_score": fusion_probability,
            "threshold": LOCKED_THRESHOLD,
            "prediction": (
                "suspicious"
                if suspicious
                else "lower_risk"
            ),
            "calibrated": False,
            "blocking": False,
        }


def fit_candidate_v2_advisory_runtime(
    training_dataframe: pd.DataFrame,
) -> CandidateV2AdvisoryRuntime:
    """
    Fit Candidate v2 once for runtime use.

    This function exists as the bridge between
    the research implementation and the future
    serialized production model artifact.

    It must not be called once per finding.
    """

    validate_locked_configuration()

    context_model = fit_context_model(
        training_dataframe
    )

    text_model = fit_text_probe(
        training_dataframe
    )

    return CandidateV2AdvisoryRuntime(
        context_model=context_model,
        text_model=text_model,
    )
