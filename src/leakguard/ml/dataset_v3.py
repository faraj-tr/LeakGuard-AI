import base64
import random
import string
import uuid
from pathlib import Path

import pandas as pd

from leakguard.ml.context_features import (
    extract_context_features,
)


DATASET_V3_SEED = 1337
DEFAULT_SAMPLES_PER_CLASS = 1000


POSITIVE_TYPES = (
    "random_secret",
    "passphrase_secret",
    "jwt_like_secret",
    "hex_secret",
    "uuid_shaped_secret",
    "hash_shaped_secret",
    "client_exposed_secret",
)


NEGATIVE_TYPES = (
    "uuid_identifier",
    "commit_hash",
    "artifact_digest",
    "public_identifier",
    "secret_reference",
    "placeholder",
    "documentation_jwt",
    "safe_phrase",
    "frontend_public_value",
    "normal_config",
)


SENSITIVE_NAMES = (
    "api_key",
    "access_token",
    "client_secret",
    "service_password",
    "database_password",
    "signing_secret",
)


NEUTRAL_NAMES = (
    "value",
    "setting",
    "runtime_data",
    "payload",
    "material",
    "result",
    "connector_value",
    "session_data",
)


PASS_PHRASE_WORDS = (
    "amber",
    "bridge",
    "canyon",
    "crystal",
    "forest",
    "harbor",
    "island",
    "lantern",
    "meadow",
    "meteor",
    "ocean",
    "orbit",
    "silver",
    "summit",
    "timber",
    "voyage",
    "winter",
)


SAFE_PHRASE_WORDS = (
    "enable",
    "preview",
    "public",
    "release",
    "stable",
    "service",
    "region",
    "default",
    "application",
    "runtime",
    "development",
    "production",
)


def random_text(
    rng: random.Random,
    alphabet: str,
    length: int,
) -> str:
    return "".join(
        rng.choice(alphabet)
        for _ in range(length)
    )


def random_hex(
    rng: random.Random,
    length: int,
) -> str:
    return random_text(
        rng,
        string.digits + "abcdef",
        length,
    )


def random_base64url(
    rng: random.Random,
    byte_length: int,
) -> str:
    raw = bytes(
        rng.randrange(0, 256)
        for _ in range(byte_length)
    )

    return (
        base64.urlsafe_b64encode(raw)
        .decode("ascii")
        .rstrip("=")
    )


def random_uuid(
    rng: random.Random,
) -> str:
    return str(
        uuid.UUID(
            int=rng.getrandbits(128)
        )
    )


def choose_name(
    rng: random.Random,
    sensitive_probability: float,
) -> str:
    if rng.random() < sensitive_probability:
        return rng.choice(
            SENSITIVE_NAMES
        )

    return rng.choice(
        NEUTRAL_NAMES
    )


def generate_passphrase(
    rng: random.Random,
) -> str:
    words = [
        rng.choice(
            PASS_PHRASE_WORDS
        )
        for _ in range(
            rng.choice((4, 5, 6))
        )
    ]

    separator = rng.choice(
        ("-", ".", " ")
    )

    return separator.join(
        words
    )


def generate_safe_phrase(
    rng: random.Random,
) -> str:
    words = [
        rng.choice(
            SAFE_PHRASE_WORDS
        )
        for _ in range(
            rng.choice((4, 5))
        )
    ]

    separator = rng.choice(
        ("-", " ")
    )

    return separator.join(
        words
    )


def generate_jwt_like(
    rng: random.Random,
) -> str:
    return ".".join(
        (
            random_base64url(
                rng,
                12,
            ),
            random_base64url(
                rng,
                20,
            ),
            random_base64url(
                rng,
                18,
            ),
        )
    )


def generate_positive_sample(
    index: int,
    rng: random.Random,
) -> dict:
    sample_type = POSITIVE_TYPES[
        index % len(
            POSITIVE_TYPES
        )
    ]

    variable_name = choose_name(
        rng=rng,
        sensitive_probability=0.45,
    )

    framework = "none"

    if sample_type == "random_secret":
        value = random_text(
            rng,
            (
                string.ascii_letters
                + string.digits
                + "_-!@#$%"
            ),
            32,
        )

    elif sample_type == "passphrase_secret":
        value = generate_passphrase(
            rng
        )

    elif sample_type == "jwt_like_secret":
        value = generate_jwt_like(
            rng
        )

    elif sample_type == "hex_secret":
        value = random_hex(
            rng,
            rng.choice(
                (32, 40, 48, 64)
            ),
        )

    elif sample_type == "uuid_shaped_secret":
        value = random_uuid(
            rng
        )

    elif sample_type == "hash_shaped_secret":
        value = random_hex(
            rng,
            rng.choice(
                (40, 64)
            ),
        )

    elif sample_type == "client_exposed_secret":
        framework = rng.choice(
            (
                "Vite",
                "Next.js",
            )
        )

        if framework == "Vite":
            variable_name = rng.choice(
                (
                    "VITE_API_KEY",
                    "VITE_CLIENT_SECRET",
                )
            )
        else:
            variable_name = rng.choice(
                (
                    "NEXT_PUBLIC_API_KEY",
                    "NEXT_PUBLIC_ACCESS_TOKEN",
                )
            )

        value = random_text(
            rng,
            (
                string.ascii_letters
                + string.digits
                + "_-"
            ),
            36,
        )

    else:
        raise ValueError(
            f"Unknown positive type: "
            f"{sample_type}"
        )

    return {
        "variable_name": variable_name,
        "value": value,
        "label": 1,
        "sample_type": sample_type,
        "framework": framework,
        "source": "synthetic_v3",
    }


def generate_negative_sample(
    index: int,
    rng: random.Random,
) -> dict:
    sample_type = NEGATIVE_TYPES[
        index % len(
            NEGATIVE_TYPES
        )
    ]

    framework = "none"

    if sample_type == "uuid_identifier":
        variable_name = rng.choice(
            (
                "request_id",
                "trace_id",
                "event_uuid",
            )
        )

        value = random_uuid(
            rng
        )

    elif sample_type == "commit_hash":
        variable_name = "commit_sha"

        value = random_hex(
            rng,
            40,
        )

    elif sample_type == "artifact_digest":
        variable_name = rng.choice(
            (
                "artifact_digest",
                "checksum",
                "image_digest",
            )
        )

        value = random_hex(
            rng,
            64,
        )

    elif sample_type == "public_identifier":
        variable_name = rng.choice(
            (
                "public_id",
                "customer_reference",
                "build_id",
            )
        )

        value = random_text(
            rng,
            (
                string.ascii_uppercase
                + string.digits
            ),
            26,
        )

    elif sample_type == "secret_reference":
        variable_name = rng.choice(
            SENSITIVE_NAMES
        )

        value = rng.choice(
            (
                "${API_KEY}",
                "${DATABASE_PASSWORD}",
                "$env:ACCESS_TOKEN",
                "process.env.CLIENT_SECRET",
                "vault://application/key",
                "%SERVICE_TOKEN%",
            )
        )

    elif sample_type == "placeholder":
        variable_name = rng.choice(
            SENSITIVE_NAMES
        )

        value = rng.choice(
            (
                "YOUR_API_KEY_HERE",
                "EXAMPLE_ONLY_DO_NOT_USE",
                "replace-me",
                "sample-secret-value",
                "<redacted>",
                "TOKEN_PLACEHOLDER",
            )
        )

    elif sample_type == "documentation_jwt":
        variable_name = rng.choice(
            (
                "jwt_example",
                "token_example",
                "documentation_token",
            )
        )

        value = generate_jwt_like(
            rng
        )

    elif sample_type == "safe_phrase":
        variable_name = rng.choice(
            (
                "deployment_mode",
                "application_setting",
                "release_description",
            )
        )

        value = generate_safe_phrase(
            rng
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
                "VITE_PUBLIC_REGION"
            )
        else:
            variable_name = (
                "NEXT_PUBLIC_RELEASE_CHANNEL"
            )

        value = rng.choice(
            (
                "stable",
                "preview",
                "eu-west",
                "public-dashboard",
            )
        )

    elif sample_type == "normal_config":
        variable_name = rng.choice(
            (
                "log_level",
                "environment",
                "service_url",
                "feature_mode",
            )
        )

        value = rng.choice(
            (
                "debug",
                "production",
                "https://example.test/api",
                "enabled",
            )
        )

    else:
        raise ValueError(
            f"Unknown negative type: "
            f"{sample_type}"
        )

    return {
        "variable_name": variable_name,
        "value": value,
        "label": 0,
        "sample_type": sample_type,
        "framework": framework,
        "source": "synthetic_v3",
    }


def add_features(
    sample: dict,
) -> dict:
    features = extract_context_features(
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


def generate_synthetic_dataset_v3(
    samples_per_class: int = (
        DEFAULT_SAMPLES_PER_CLASS
    ),
    seed: int = DATASET_V3_SEED,
) -> pd.DataFrame:
    """
    Generate Candidate v2 training data.

    Dataset v3 intentionally gives multiple
    contextual structures support in both
    classes to reduce shortcut learning.
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
        records.append(
            add_features(
                generate_positive_sample(
                    index=index,
                    rng=rng,
                )
            )
        )

        records.append(
            add_features(
                generate_negative_sample(
                    index=index,
                    rng=rng,
                )
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
            f"LGV3-{index:06d}"
            for index in range(
                1,
                len(dataframe) + 1,
            )
        ],
    )

    return dataframe


def save_synthetic_dataset_v3(
    output_path: Path,
    samples_per_class: int = (
        DEFAULT_SAMPLES_PER_CLASS
    ),
    seed: int = DATASET_V3_SEED,
) -> pd.DataFrame:
    dataframe = (
        generate_synthetic_dataset_v3(
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
