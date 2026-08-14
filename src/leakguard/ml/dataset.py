import random
import string
import uuid
from pathlib import Path

import pandas as pd

from leakguard.ml.features import extract_ml_features


DEFAULT_SEED = 42
DEFAULT_SAMPLES_PER_CLASS = 500


POSITIVE_SECRET_TYPES = (
    "password",
    "api_key",
    "access_token",
    "database_credential",
    "client_exposed_secret",
)


NEGATIVE_SAMPLE_TYPES = (
    "placeholder",
    "ui_text",
    "uuid",
    "url",
    "color",
    "public_identifier",
    "filename",
    "normal_config",
    "frontend_public_value",
)


SENSITIVE_VARIABLE_NAMES = (
    "password",
    "db_password",
    "api_key",
    "client_secret",
    "access_token",
    "auth_token",
    "database_password",
)


NEUTRAL_VARIABLE_NAMES = (
    "x",
    "value",
    "data",
    "config_value",
    "setting",
    "payload",
    "result",
)


def random_characters(
    rng: random.Random,
    length: int,
) -> str:
    """
    Generate deterministic synthetic random-looking
    characters.

    These values are artificial training data and
    are never validated against real services.
    """

    alphabet = (
        string.ascii_letters
        + string.digits
    )

    return "".join(
        rng.choice(alphabet)
        for _ in range(length)
    )


def random_password(
    rng: random.Random,
) -> str:
    """
    Generate a synthetic password-like value
    containing multiple character categories.
    """

    characters = [
        rng.choice(string.ascii_lowercase),
        rng.choice(string.ascii_uppercase),
        rng.choice(string.digits),
        rng.choice("!@#$%_-"),
    ]

    characters.extend(
        rng.choice(
            string.ascii_letters
            + string.digits
            + "!@#$%_-"
        )
        for _ in range(16)
    )

    rng.shuffle(
        characters
    )

    return "".join(
        characters
    )


def generate_secret_value(
    secret_type: str,
    rng: random.Random,
) -> str:
    """
    Generate a synthetic value for a requested
    secret category.
    """

    if secret_type == "password":
        return random_password(
            rng
        )

    if secret_type == "api_key":
        prefix = rng.choice(
            (
                "key_",
                "api_",
                "svc_",
                "",
            )
        )

        return (
            prefix
            + random_characters(
                rng,
                28,
            )
        )

    if secret_type == "access_token":
        return (
            random_characters(
                rng,
                18,
            )
            + "."
            + random_characters(
                rng,
                18,
            )
        )

    if secret_type == "database_credential":
        return random_password(
            rng
        )

    if secret_type == "client_exposed_secret":
        return random_characters(
            rng,
            32,
        )

    raise ValueError(
        f"Unsupported secret type: {secret_type}"
    )


def choose_positive_variable(
    secret_type: str,
    index: int,
    rng: random.Random,
) -> str:
    """
    Choose variable names for positive samples.

    Some true secrets intentionally use neutral
    variable names so the model cannot rely only
    on names such as password or api_key.
    """

    if secret_type == "client_exposed_secret":

        if index % 2 == 0:
            return "VITE_API_KEY"

        return "NEXT_PUBLIC_ACCESS_TOKEN"

    # Roughly one third of secret samples use
    # intentionally unhelpful variable names.
    if index % 3 == 0:
        return rng.choice(
            NEUTRAL_VARIABLE_NAMES
        )

    return rng.choice(
        SENSITIVE_VARIABLE_NAMES
    )


def generate_positive_sample(
    index: int,
    rng: random.Random,
) -> dict:
    """
    Generate one synthetic secret sample.
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
        choose_positive_variable(
            secret_type=secret_type,
            index=index,
            rng=rng,
        )
    )

    value = generate_secret_value(
        secret_type=secret_type,
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
        "source": "synthetic",
    }


def generate_negative_sample(
    index: int,
    rng: random.Random,
) -> dict:
    """
    Generate one synthetic non-secret sample.

    Some negative examples deliberately use
    sensitive-looking variable names to teach
    the model about placeholders and context.
    """

    sample_type = (
        NEGATIVE_SAMPLE_TYPES[
            index
            % len(
                NEGATIVE_SAMPLE_TYPES
            )
        ]
    )

    framework = "none"

    if sample_type == "placeholder":

        examples = (
            (
                "api_key",
                "your-api-key-here",
            ),
            (
                "password",
                "replace-me",
            ),
            (
                "client_secret",
                "not-configured",
            ),
            (
                "access_token",
                "example-token",
            ),
        )

        variable_name, value = (
            examples[
                index
                % len(examples)
            ]
        )

    elif sample_type == "ui_text":

        examples = (
            "Please enter your password",
            "API key is required",
            "Authentication failed",
            "Enter your access token",
        )

        variable_name = "message"

        value = examples[
            index
            % len(examples)
        ]

    elif sample_type == "uuid":

        variable_name = "request_id"

        value = str(
            uuid.UUID(
                int=rng.getrandbits(
                    128
                )
            )
        )

    elif sample_type == "url":

        variable_name = "service_url"

        value = rng.choice(
            (
                "https://example.com/api",
                "https://localhost:8000",
                "https://docs.example.org",
            )
        )

    elif sample_type == "color":

        variable_name = "theme_color"

        value = rng.choice(
            (
                "#0866C6",
                "#FFDCE6",
                "#F7F9FC",
            )
        )

    elif sample_type == "public_identifier":

        variable_name = "public_id"

        value = (
            "PUB-"
            + random_characters(
                rng,
                12,
            )
        )

    elif sample_type == "filename":

        variable_name = "config_file"

        value = rng.choice(
            (
                "settings.json",
                "application.yaml",
                "config.production.json",
            )
        )

    elif sample_type == "normal_config":

        variable_name = rng.choice(
            (
                "environment",
                "region",
                "log_level",
                "app_name",
            )
        )

        value = rng.choice(
            (
                "production",
                "development",
                "eu-west",
                "INFO",
                "LeakGuard",
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
                "Dashboard",
                "Security Portal",
            )
        )

    else:
        raise ValueError(
            "Unsupported negative "
            f"sample type: {sample_type}"
        )

    return {
        "variable_name": variable_name,
        "value": value,
        "label": 0,
        "sample_type": sample_type,
        "framework": framework,
        "source": "synthetic",
    }


def add_features(
    sample: dict,
) -> dict:
    """
    Add LeakGuard numerical ML features
    to a dataset sample.
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


def generate_synthetic_dataset(
    samples_per_class: int = (
        DEFAULT_SAMPLES_PER_CLASS
    ),
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """
    Generate a balanced synthetic dataset.

    Label:
        1 = secret
        0 = non-secret
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
            generate_positive_sample(
                index=index,
                rng=rng,
            )
        )

        negative = (
            generate_negative_sample(
                index=index,
                rng=rng,
            )
        )

        records.append(
            add_features(
                positive
            )
        )

        records.append(
            add_features(
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
            f"LGV1-{index:06d}"
            for index in range(
                1,
                len(dataframe) + 1,
            )
        ],
    )

    return dataframe


def save_synthetic_dataset(
    output_path: Path,
    samples_per_class: int = (
        DEFAULT_SAMPLES_PER_CLASS
    ),
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """
    Generate and save LeakGuard Synthetic
    Dataset v1 as a CSV file.
    """

    dataframe = (
        generate_synthetic_dataset(
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