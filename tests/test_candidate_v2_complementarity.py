from sklearn.pipeline import Pipeline

from leakguard.ml.candidate_v2_complementarity import (
    build_complementarity_frame,
    build_text_input,
    build_text_predictions,
    build_text_probe_pipeline,
    evaluate_text_probe,
    get_outcome_summary,
)
from leakguard.ml.challenge import (
    generate_challenge_dataset,
)
from leakguard.ml.context_diagnostics import (
    build_context_predictions,
)
from leakguard.ml.dataset_v3 import (
    generate_synthetic_dataset_v3,
)


def create_data():
    training = (
        generate_synthetic_dataset_v3(
            samples_per_class=140,
            seed=1337,
        )
    )

    development = (
        generate_challenge_dataset(
            samples_per_class=50,
            seed=2026,
        )
    )

    return training, development


def test_text_input_matches_dataset_size():
    training, _ = create_data()

    text = build_text_input(
        training
    )

    assert len(text) == len(
        training
    )


def test_text_probe_pipeline_is_created():
    model = (
        build_text_probe_pipeline()
    )

    assert isinstance(
        model,
        Pipeline,
    )

    assert "tfidf" in (
        model.named_steps
    )

    assert "classifier" in (
        model.named_steps
    )


def test_text_predictions_match_development_size():
    training, development = (
        create_data()
    )

    results = (
        build_text_predictions(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    assert len(results) == len(
        development
    )

    assert (
        "text_prediction"
        in results.columns
    )

    assert (
        "text_probability"
        in results.columns
    )


def test_text_probe_metrics_are_valid():
    training, development = (
        create_data()
    )

    result = evaluate_text_probe(
        training_dataframe=training,
        development_dataframe=development,
    )

    assert (
        0.0
        <= result.accuracy
        <= 1.0
    )

    assert (
        0.0
        <= result.f1
        <= 1.0
    )

    assert (
        0.0
        <= result.roc_auc
        <= 1.0
    )


def test_complementarity_covers_all_rows():
    training, development = (
        create_data()
    )

    context = (
        build_context_predictions(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    text = (
        build_text_predictions(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    comparison = (
        build_complementarity_frame(
            context_results=context,
            text_results=text,
        )
    )

    assert len(comparison) == len(
        development
    )

    summary = get_outcome_summary(
        comparison
    )

    assert summary[
        "count"
    ].sum() == len(
        development
    )


def test_complementarity_outcomes_are_known():
    training, development = (
        create_data()
    )

    context = (
        build_context_predictions(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    text = (
        build_text_predictions(
            training_dataframe=training,
            development_dataframe=development,
        )
    )

    comparison = (
        build_complementarity_frame(
            context_results=context,
            text_results=text,
        )
    )

    allowed = {
        "both_correct",
        "context_only_correct",
        "text_only_correct",
        "both_wrong",
    }

    assert set(
        comparison["outcome"]
    ).issubset(
        allowed
    )
