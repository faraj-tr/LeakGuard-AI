import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from leakguard.ml.locked_fusion import (
    LOCKED_MODEL_NAME,
    evaluate_locked_fusion,
    get_locked_configuration,
)


EXPECTED_FINAL_SOURCE = "final_challenge_v2"

EXPECTED_FINAL_SAMPLES = 600
EXPECTED_SECRET_SAMPLES = 300
EXPECTED_SAFE_SAMPLES = 300


def calculate_file_sha256(
    path: Path,
) -> str:
    """
    Calculate SHA-256 for the exact final
    evaluation dataset file.
    """

    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b"",
        ):
            sha256.update(
                chunk
            )

    return sha256.hexdigest()


def validate_final_dataset(
    dataframe: pd.DataFrame,
) -> None:
    """
    Validate the locked final evaluation
    dataset before benchmarking.
    """

    required_columns = {
        "sample_id",
        "variable_name",
        "value",
        "label",
        "sample_type",
        "framework",
        "source",
        "length",
        "entropy",
        "digit_ratio",
        "uppercase_ratio",
        "special_ratio",
        "has_sensitive_name",
        "is_compact",
        "has_character_variety",
    }

    missing = (
        required_columns
        - set(dataframe.columns)
    )

    if missing:
        raise ValueError(
            "Final dataset is missing "
            f"columns: {sorted(missing)}"
        )

    if len(dataframe) != EXPECTED_FINAL_SAMPLES:
        raise ValueError(
            "Unexpected final dataset size. "
            f"Expected {EXPECTED_FINAL_SAMPLES}, "
            f"received {len(dataframe)}."
        )

    secret_count = int(
        (
            dataframe["label"]
            == 1
        ).sum()
    )

    safe_count = int(
        (
            dataframe["label"]
            == 0
        ).sum()
    )

    if secret_count != EXPECTED_SECRET_SAMPLES:
        raise ValueError(
            "Unexpected secret count. "
            f"Expected {EXPECTED_SECRET_SAMPLES}, "
            f"received {secret_count}."
        )

    if safe_count != EXPECTED_SAFE_SAMPLES:
        raise ValueError(
            "Unexpected safe count. "
            f"Expected {EXPECTED_SAFE_SAMPLES}, "
            f"received {safe_count}."
        )

    sources = set(
        dataframe["source"]
        .astype(str)
    )

    if sources != {
        EXPECTED_FINAL_SOURCE
    }:
        raise ValueError(
            "Unexpected final dataset "
            f"source values: {sorted(sources)}"
        )

    labels = set(
        dataframe["label"]
        .unique()
    )

    if labels != {
        0,
        1,
    }:
        raise ValueError(
            "Final dataset must contain "
            "binary labels 0 and 1."
        )

    if dataframe[
        "sample_id"
    ].duplicated().any():
        raise ValueError(
            "Final dataset contains "
            "duplicate sample IDs."
        )


def build_final_report(
    training_dataframe: pd.DataFrame,
    final_dataframe: pd.DataFrame,
    dataset_sha256: str,
) -> dict:
    """
    Run the already locked candidate on
    the untouched final evaluation set.

    No tuning occurs here.
    """

    validate_final_dataset(
        final_dataframe
    )

    configuration = (
        get_locked_configuration()
    )

    result = (
        evaluate_locked_fusion(
            training_dataframe=(
                training_dataframe
            ),
            evaluation_dataframe=(
                final_dataframe
            ),
        )
    )

    metrics = asdict(
        result
    )

    return {
        "benchmark": (
            "LeakGuard Final "
            "Generalization Benchmark v1"
        ),
        "status": "FINAL_EVALUATION",
        "model": LOCKED_MODEL_NAME,
        "training_dataset": (
            "Synthetic Dataset v2"
        ),
        "training_samples": int(
            len(training_dataframe)
        ),
        "evaluation_dataset": (
            "Final Challenge Dataset v2"
        ),
        "evaluation_samples": int(
            len(final_dataframe)
        ),
        "evaluation_dataset_sha256": (
            dataset_sha256
        ),
        "locked_configuration": (
            configuration
        ),
        "metrics": metrics,
        "policy": {
            "used_for_training": False,
            "used_for_tuning": False,
            "weights_locked_before_test": True,
            "threshold_locked_before_test": True,
            "do_not_retune_on_result": True,
        },
        "generated_at_utc": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
    }


def save_final_report(
    report: dict,
    output_path: Path,
) -> None:
    """
    Save final benchmark report without
    silently overwriting an existing one.
    """

    if output_path.exists():
        raise FileExistsError(
            "Final benchmark report already "
            f"exists: {output_path}"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

        file.write("\n")
