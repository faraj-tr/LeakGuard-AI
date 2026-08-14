import random
import string
import uuid
from pathlib import Path

import pandas as pd

from leakguard.ml.dataset import (
    random_characters,
    random_password,
)
from leakguard.ml.features import (
    extract_ml_features,
)


V2_DEFAULT_SEED = 42
V2_DEFAULT_SAMPLES_PER_CLASS = 500


POSITIVE_SECRET_TYPES = (
    "password",
    "api_key",
    "access_token",
    "database_credential",
    "client_exposed_secret",
)


SENSITIVE_POSITIVE_NAMES = {
    "password": (
        "password",
        "user_password",
        "admin_password",
    ),
    "api_key": (
        "api_key",
        "service_api_key",
        "private_api_key",
    ),
    "access_token": (
        "access_token",
        "auth_token",
        "service_token",
    ),
    "database_credential": (
        "db_password",
        "database_password",
        "database_credential",
    ),
}


NEUTRAL_POSITIVE_NAMES = (
    "x",
    "value",
    "data",
    "config_value",
    "runtime_value",
    "payload",
    "setting",
    "result",
)


SENSITIVE_NEGATIVE_NAMES = (
    "password",
    "db_password",
    "api_key",
    "client_secret",
    "access_token",
    "auth_token",
    "service_token",
    "database_password",
)


HARD_NEGATIVE_TYPES = (
    "placeholder",
    "env_reference",
    "redacted",
    "documentation_example",
)


BENIGN_NEGATIVE_TYPES = (
    "ui_text",
    "uuid",
    "sha256",
    "checksum",
    "public_identifier",
    "build_id",
    "url",
    "normal_config",
    "frontend_public_value",
)


PASSPHRASE_WORDS = (
    "river",
    "forest",
    "silent",
    "orange",
    "planet",
    "window",
    "silver",
    "garden",
    "cloud",
    "coffee",
    "bridge",
    "summer",
    "winter",
    "falcon",
    "mountain",
    "ocean",
)


def random_hex(
    rng: random.Random,
    length: int,
) -> str:
    """
    Generate deterministic synthetic
    hexadecimal text.
    """

    alphabet = (
        string.digits
        + "abcdef"
    )

    return "".join(
        rng.choice(alphabet)
        for _ in range(length)
    )


def random_passphrase(
    rng: random.Random,
) -> str:
    """
    Generate a synthetic secret passphrase.

    Spaces are intentional so positive
    examples are not always compact.
    """

    words = [
        rng.choice(
            PASSPHRASE_WORDS
        )
        for _ in range(4)
    ]

    return " ".join(
        words
    )


def generate_v2_secret_value(
    secret_type: str,
    index: int,
    rng: random.Random,
) -> str:
    """
    Generate more diverse positive values
    than Dataset v1.

    Some values deliberately resemble benign
    identifiers so the model cannot depend
    on entropy alone.
    """

    if secret_type == "password":

        if index % 4 == 0:
            return random_passphrase(
                rng
            )

        return random_password(
            rng
        )

    if secret_type == "api_key":

        if index % 3 == 0:
            return random_hex(
                rng,
                32,
            )

        return (
            "lgk_"
            + random_characters(
                rng,
                28,
            )
        )

    if secret_type == "access_token":

        if index % 3 == 0:
            return random_hex(
                rng,
                40,
            )

        return (
            random_characters(
                rng,
                16,
            )
            + "."
            + random_characters(
                rng,
                16,
            )
        )

    if secret_type == "database_credential":

        if index % 5 == 0:
            return random_passphrase(
                rng
            )

        return random_password(
            rng
        )

    if secret_type == "client_exposed_secret":

        if index % 3 == 0:
            return random_hex(
                rng,
                32,
            )

        return (
            "client_"
            + random_characters(
                rng,
                26,
            )
        )

    raise ValueError(
        f"Unsupported secret type: "
        f"{secret_type}"
    )


def choose_v2_positive_variable(
    secret_type: str,
    index: int,
    samples_per_class: int,
    rng: random.Random,
) -> str:
    """
    Approximately half of true secrets use
    sensitive names and half use neutral names.

    This directly reduces variable-name bias.
    """

    sensitive_cutoff = (
        samples_per_class // 2
    )

    use_sensitive_name = (
        index < sensitive_cutoff
    )

    if secret_type == "client_exposed_secret":

        if use_sensitive_name:

            return rng.choice(
                (
                    "VITE_API_KEY",
                    "NEXT_PUBLIC_ACCESS_TOKEN",
                )
            )

        return rng.choice(
            (
                "VITE_CONFIG_VALUE",
                "NEXT_PUBLIC_RUNTIME_VALUE",
            )
        )

    if use_sensitive_name:

        return rng.choice(
            SENSITIVE_POSITIVE_NAMES[
                secret_type
            ]
        )

    return rng.choice(
        NEUTRAL_POSITIVE_NAMES
    )


def generate_v2_positive_sample(
    index: int,
    samples_per_class: int,
    rng: random.Random,
) -> dict:
    """
    Generate one positive Dataset v2 sample.
    """

    secret_type = (
        POSITIVE_SECRET_TYPES[
            index
            % len(
                POSITIVE_SECRET_TYPES
            )
        ]
    )

    variable_name = (
        choose_v2_positive_variable(
            secret_type=secret_type,
            index=index,
            samples_per_class=(
                samples_per_class
            ),
            rng=rng,
        )
    )

    value = generate_v2_secret_value(
        secret_type=secret_type,
        index=index,
        rng=rng,
    )

    framework = "none"

    if variable_name.startswith(
        "VITE_"
    ):
        framework = "Vite"

    elif variable_name.startswith(
        "NEXT_PUBLIC_"
    ):
        framework = "Next.js"

    return {
        "variable_name": variable_name,
        "value": value,
        "label": 1,
        "sample_type": secret_type,
        "framework": framework,
        "source": "synthetic_v2",
    }


def generate_hard_negative(
    index: int,
    rng: random.Random,
) -> dict:
    """
    Generate a safe sample that intentionally
    has a sensitive-looking variable name.

    These examples fight shortcut learning.
    """

    sample_type = (
        HARD_NEGATIVE_TYPES[
            index
            % len(
                HARD_NEGATIVE_TYPES
            )
        ]
    )

    variable_name = rng.choice(
        SENSITIVE_NEGATIVE_NAMES
    )

    if sample_type == "placeholder":

        value = rng.choice(
            (
                "your-api-key-here",
                "replace-me",
                "change-this-value",
                "example-token",
                "your-password-here",
            )
        )

    elif sample_type == "env_reference":

        value = rng.choice(
            (
                "${API_KEY}",
                "${DB_PASSWORD}",
                "$ACCESS_TOKEN",
                "process.env.API_KEY",
                "env.API_KEY",
                "os.getenv(API_KEY)",
            )
        )

    elif sample_type == "redacted":

        value = rng.choice(
            (
                "<redacted>",
                "***REDACTED***",
                "[hidden]",
                "not-configured",
                "removed-for-security",
            )
        )

    elif sample_type == "documentation_example":

        value = rng.choice(
            (
                "example-only-value",
                "demo-credential",
                "sample-secret-value",
                "documentation-token",
                "fake-value-for-docs",
            )
        )

    else:
        raise ValueError(
            "Unsupported hard negative "
            f"type: {sample_type}"
        )

    return {
        "variable_name": variable_name,
        "value": value,
        "label": 0,
        "sample_type": sample_type,
        "framework": "none",
        "source": "synthetic_v2",
    }


def generate_benign_negative(
    index: int,
    rng: random.Random,
) -> dict:
    """
    Generate a benign sample.

    Several categories intentionally have
    high entropy or long compact values.
    """

    sample_type = (
        BENIGN_NEGATIVE_TYPES[
            index
            % len(
                BENIGN_NEGATIVE_TYPES
            )
        ]
    )

    framework = "none"

    if sample_type == "ui_text":

        variable_name = "message"

        value = rng.choice(
            (
                "Please enter your password",
                "Authentication successful",
                "API key is required",
                "Your session has expired",
                "Enter your access token",
            )
        )

    elif sample_type == "uuid":

        variable_name = "request_id"

        value = str(
            uuid.UUID(
                int=rng.getrandbits(
                    128
                )
            )
        )

    elif sample_type == "sha256":

        variable_name = "file_hash"

        value = random_hex(
            rng,
            64,
        )

    elif sample_type == "checksum":

        variable_name = "checksum"

        value = random_hex(
            rng,
            40,
        )

    elif sample_type == "public_identifier":

        variable_name = "public_id"

        value = (
            "PUB-"
            + random_characters(
                rng,
                20,
            )
        )

    elif sample_type == "build_id":

        variable_name = "build_id"

        value = random_characters(
            rng,
            28,
        )

    elif sample_type == "url":

        variable_name = "service_url"

        value = rng.choice(
            (
                "https://example.com/api",
                "https://docs.example.org",
                "https://localhost:8000",
                "https://app.example.com/dashboard",
            )
        )

    elif sample_type == "normal_config":

        variable_name = rng.choice(
            (
                "environment",
                "region",
                "log_level",
                "app_name",
                "timezone",
            )
        )

        value = rng.choice(
            (
                "production",
                "development",
                "eu-west",
                "INFO",
                "LeakGuard",
                "UTC",
            )
        )

    elif sample_type == "frontend_public_value":

        framework = rng.choice(
            (
                "Vite",
                "Next.js",
            )
        )

        if framework == "Vite":
            variable_name = (
                "VITE_APP_TITLE"
            )

        else:
            variable_name = (
                "NEXT_PUBLIC_APP_NAME"
            )

        value = rng.choice(
            (
                "LeakGuard Demo",
                "Security Portal",
                "Dashboard",
                "Developer Console",
            )
        )

    else:
        raise ValueError(
            "Unsupported benign negative "
            f"type: {sample_type}"
        )

    return {
        "variable_name": variable_name,
        "value": value,
        "label": 0,
        "sample_type": sample_type,
        "framework": framework,
        "source": "synthetic_v2",
    }


def generate_v2_negative_sample(
    index: int,
    samples_per_class: int,
    rng: random.Random,
) -> dict:
    """
    Forty percent of negative examples use
    intentionally sensitive variable names.

    The remaining sixty percent contain
    normal and high-entropy benign values.
    """

    hard_negative_count = int(
        samples_per_class
        * 0.40
    )

    if index < hard_negative_count:

        return generate_hard_negative(
            index=index,
            rng=rng,
        )

    benign_index = (
        index
        - hard_negative_count
    )

    return generate_benign_negative(
        index=benign_index,
        rng=rng,
    )


def add_v2_features(
    sample: dict,
) -> dict:
    """
    Add LeakGuard ML features to a
    Dataset v2 record.
    """

    features = extract_ml_features(
        variable_name=sample[
            "variable_name"
        ],
        value=sample[
            "value"
        ],
    )

    return {
        **sample,
        **features,
    }


def generate_synthetic_dataset_v2(
    samples_per_class: int = (
        V2_DEFAULT_SAMPLES_PER_CLASS
    ),
    seed: int = V2_DEFAULT_SEED,
) -> pd.DataFrame:
    """
    Generate LeakGuard Synthetic Dataset v2.

    Dataset design:
        50% positive / 50% negative.

        Positive samples:
            roughly 50% sensitive names
            roughly 50% neutral names.

        Negative samples:
            40% sensitive-name hard negatives
            60% benign/contextual negatives.
    """

    if samples_per_class <= 0:

        raise ValueError(
            "samples_per_class must "
            "be greater than zero."
        )

    rng = random.Random(
        seed
    )

    records = []

    for index in range(
        samples_per_class
    ):

        positive = (
            generate_v2_positive_sample(
                index=index,
                samples_per_class=(
                    samples_per_class
                ),
                rng=rng,
            )
        )

        negative = (
            generate_v2_negative_sample(
                index=index,
                samples_per_class=(
                    samples_per_class
                ),
                rng=rng,
            )
        )

        records.append(
            add_v2_features(
                positive
            )
        )

        records.append(
            add_v2_features(
                negative
            )
        )

    dataframe = pd.DataFrame(
        records
    )

    dataframe = (
        dataframe
        .sample(
            frac=1,
            random_state=seed,
        )
        .reset_index(
            drop=True
        )
    )

    dataframe.insert(
        0,
        "sample_id",
        [
            f"LGV2-{index:06d}"
            for index in range(
                1,
                len(dataframe) + 1,
            )
        ],
    )

    return dataframe


def save_synthetic_dataset_v2(
    output_path: Path,
    samples_per_class: int = (
        V2_DEFAULT_SAMPLES_PER_CLASS
    ),
    seed: int = V2_DEFAULT_SEED,
) -> pd.DataFrame:
    """
    Generate and save LeakGuard
    Synthetic Dataset v2.
    """

    dataframe = (
        generate_synthetic_dataset_v2(
            samples_per_class=(
                samples_per_class
            ),
            seed=seed,
        )
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    return dataframe