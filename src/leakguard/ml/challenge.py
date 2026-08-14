import base64
import random
import string
import uuid
from pathlib import Path

import pandas as pd

from leakguard.ml.features import extract_ml_features


CHALLENGE_SEED = 2026
CHALLENGE_SAMPLES_PER_CLASS = 200


POSITIVE_TYPES = (
    "hex_secret",
    "jwt_like_secret",
    "base64_secret",
    "passphrase_secret",
    "opaque_secret",
)


NEGATIVE_TYPES = (
    "git_commit_hash",
    "artifact_digest",
    "trace_uuid",
    "public_reference",
    "documentation_placeholder",
    "secret_reference",
    "public_url",
    "frontend_public_config",
)


NEUTRAL_SECRET_NAMES = (
    "runtime_blob",
    "opaque_value",
    "integration_value",
    "material",
    "session_material",
    "runtime_data",
    "deployment_value",
)


SENSITIVE_SECRET_NAMES = (
    "private_token_value",
    "backend_auth_secret",
    "service_credential",
    "deployment_secret",
    "integration_token",
)


PASSPHRASE_WORDS = (
    "amber",
    "harbor",
    "meteor",
    "lantern",
    "canyon",
    "velvet",
    "pioneer",
    "island",
    "comet",
    "anchor",
    "meadow",
    "sunrise",
    "crystal",
    "voyage",
    "timber",
    "desert",
)


def random_text(
    rng: random.Random,
    alphabet: str,
    length: int,
) -> str:
    """
    Generate deterministic synthetic text.
    """

    return "".join(
        rng.choice(alphabet)
        for _ in range(length)
    )


def random_hex(
    rng: random.Random,
    length: int,
) -> str:
    """
    Generate a synthetic hexadecimal value.
    """

    return random_text(
        rng=rng,
        alphabet=(
            string.digits
            + "abcdef"
        ),
        length=length,
    )


def random_base64url(
    rng: random.Random,
    byte_length: int,
) -> str:
    """
    Generate deterministic synthetic
    Base64 URL-safe text.
    """

    raw_bytes = bytes(
        rng.randrange(
            0,
            256,
        )
        for _ in range(
            byte_length
        )
    )

    return (
        base64.urlsafe_b64encode(
            raw_bytes
        )
        .decode("ascii")
        .rstrip("=")
    )


def generate_secret_value(
    sample_type: str,
    rng: random.Random,
) -> str:
    """
    Generate challenge secret values using
    patterns that differ from Dataset v2.
    """

    if sample_type == "hex_secret":

        return random_hex(
            rng,
            48,
        )

    if sample_type == "jwt_like_secret":

        header = random_base64url(
            rng,
            10,
        )

        payload = random_base64url(
            rng,
            18,
        )

        signature = random_base64url(
            rng,
            16,
        )

        return (
            f"{header}."
            f"{payload}."
            f"{signature}"
        )

    if sample_type == "base64_secret":

        value = random_base64url(
            rng,
            32,
        )

        return (
            f"{value}=="
        )

    if sample_type == "passphrase_secret":

        words = [
            rng.choice(
                PASSPHRASE_WORDS
            )
            for _ in range(5)
        ]

        return "-".join(
            words
        )

    if sample_type == "opaque_secret":

        alphabet = (
            string.ascii_letters
            + string.digits
            + "_-!@"
        )

        return random_text(
            rng=rng,
            alphabet=alphabet,
            length=36,
        )

    raise ValueError(
        "Unsupported positive challenge "
        f"type: {sample_type}"
    )


def choose_secret_variable_name(
    index: int,
    rng: random.Random,
) -> str:
    """
    Most challenge secrets use neutral names.

    This prevents the model from relying
    primarily on obvious credential names.
    """

    if index % 4 == 0:

        return rng.choice(
            SENSITIVE_SECRET_NAMES
        )

    return rng.choice(
        NEUTRAL_SECRET_NAMES
    )


def generate_positive_sample(
    index: int,
    rng: random.Random,
) -> dict:
    """
    Generate one out-of-distribution
    synthetic secret.
    """

    sample_type = (
        POSITIVE_TYPES[
            index
            % len(
                POSITIVE_TYPES
            )
        ]
    )

    variable_name = (
        choose_secret_variable_name(
            index=index,
            rng=rng,
        )
    )

    value = generate_secret_value(
        sample_type=sample_type,
        rng=rng,
    )

    return {
        "variable_name": variable_name,
        "value": value,
        "label": 1,
        "sample_type": sample_type,
        "framework": "none",
        "source": "challenge_v1",
    }


def generate_negative_sample(
    index: int,
    rng: random.Random,
) -> dict:
    """
    Generate a safe challenge sample.

    Several safe values intentionally look
    random or credential-related.
    """

    sample_type = (
        NEGATIVE_TYPES[
            index
            % len(
                NEGATIVE_TYPES
            )
        ]
    )

    framework = "none"

    if sample_type == "git_commit_hash":

        variable_name = "commit_sha"

        value = random_hex(
            rng,
            40,
        )

    elif sample_type == "artifact_digest":

        variable_name = (
            "artifact_digest"
        )

        value = random_hex(
            rng,
            64,
        )

    elif sample_type == "trace_uuid":

        variable_name = (
            "trace_identifier"
        )

        value = str(
            uuid.UUID(
                int=rng.getrandbits(
                    128
                )
            )
        )

    elif sample_type == "public_reference":

        variable_name = (
            "customer_public_ref"
        )

        value = (
            "REF_"
            + random_text(
                rng=rng,
                alphabet=(
                    string.ascii_uppercase
                    + string.digits
                ),
                length=24,
            )
        )

    elif sample_type == (
        "documentation_placeholder"
    ):

        variable_name = rng.choice(
            (
                "api_key_example",
                "password_template",
                "token_placeholder",
                "client_secret_example",
            )
        )

        value = rng.choice(
            (
                "YOUR_REAL_KEY_GOES_HERE",
                "INSERT_PASSWORD_HERE",
                "EXAMPLE_ONLY_DO_NOT_USE",
                "TOKEN_PLACEHOLDER_VALUE",
            )
        )

    elif sample_type == "secret_reference":

        variable_name = rng.choice(
            (
                "api_key_reference",
                "password_reference",
                "token_reference",
                "secret_reference",
            )
        )

        value = rng.choice(
            (
                "${SECRET_FROM_VAULT}",
                "$env:API_KEY",
                "%SERVICE_TOKEN%",
                "vault://application/key",
            )
        )

    elif sample_type == "public_url":

        variable_name = "documentation_url"

        value = rng.choice(
            (
                "https://docs.example.test/token/setup",
                "https://portal.example.test/auth/help",
                "https://example.test/api/reference",
                "https://developer.example.test/keys",
            )
        )

    elif sample_type == (
        "frontend_public_config"
    ):

        framework = rng.choice(
            (
                "Vite",
                "Next.js",
            )
        )

        if framework == "Vite":

            variable_name = (
                "VITE_RELEASE_CHANNEL"
            )

        else:

            variable_name = (
                "NEXT_PUBLIC_DOCS_HOST"
            )

        value = rng.choice(
            (
                "stable",
                "preview",
                "docs.example.test",
                "public-dashboard",
            )
        )

    else:

        raise ValueError(
            "Unsupported negative "
            f"challenge type: {sample_type}"
        )

    return {
        "variable_name": variable_name,
        "value": value,
        "label": 0,
        "sample_type": sample_type,
        "framework": framework,
        "source": "challenge_v1",
    }


def add_features(
    sample: dict,
) -> dict:
    """
    Add the same numerical features used by
    the LeakGuard baseline models.
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


def generate_challenge_dataset(
    samples_per_class: int = (
        CHALLENGE_SAMPLES_PER_CLASS
    ),
    seed: int = CHALLENGE_SEED,
) -> pd.DataFrame:
    """
    Generate LeakGuard Challenge Dataset v1.

    This dataset is intentionally generated
    separately from the training Dataset v2.

    Labels:
        1 = secret
        0 = safe
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
            f"LGC1-{index:06d}"
            for index in range(
                1,
                len(dataframe) + 1,
            )
        ],
    )

    return dataframe


def save_challenge_dataset(
    output_path: Path,
    samples_per_class: int = (
        CHALLENGE_SAMPLES_PER_CLASS
    ),
    seed: int = CHALLENGE_SEED,
) -> pd.DataFrame:
    """
    Generate and save Challenge Dataset v1.
    """

    dataframe = (
        generate_challenge_dataset(
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