import base64
import random
import string
import uuid
from pathlib import Path

import pandas as pd

from leakguard.ml.context_features import (
    extract_context_features,
)


DEVSET_SEED = 260815
DEFAULT_SAMPLES_PER_CLASS = 300


POSITIVE_TYPES = (
    "alternate_random_secret",
    "alternate_passphrase_secret",
    "alternate_jwt_secret",
    "alternate_hex_secret",
    "alternate_uuid_secret",
    "alternate_base64_secret",
    "alternate_client_exposed_secret",
)


NEGATIVE_TYPES = (
    "alternate_uuid_identifier",
    "alternate_source_hash",
    "alternate_checksum",
    "alternate_secret_reference",
    "alternate_placeholder",
    "alternate_documentation_jwt",
    "alternate_safe_phrase",
    "alternate_public_identifier",
    "alternate_frontend_public_config",
)


SECRET_NAMES = (
    "auth_material",
    "service_credential",
    "private_token",
    "backend_key",
    "session_secret",
    "connector_credential",
)


NEUTRAL_NAMES = (
    "runtime_value",
    "payload_data",
    "integration_data",
    "application_value",
    "session_material",
    "opaque_data",
)


IDENTIFIER_NAMES = (
    "session_id",
    "credential_id",
    "private_reference",
    "auth_reference",
)


SAFE_IDENTIFIER_NAMES = (
    "request_identifier",
    "operation_uuid",
    "correlation_id",
    "resource_reference",
)


PASS_PHRASE_WORDS = (
    "acorn",
    "beacon",
    "cedar",
    "delta",
    "ember",
    "falcon",
    "garden",
    "horizon",
    "ivory",
    "jungle",
    "kernel",
    "lagoon",
    "marble",
    "nebula",
    "prairie",
    "quartz",
    "river",
    "saffron",
)


SAFE_PHRASE_WORDS = (
    "application",
    "service",
    "feature",
    "release",
    "region",
    "preview",
    "runtime",
    "default",
    "enabled",
    "public",
    "staging",
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
        string.hexdigits.lower()[:16],
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


def random_tag(
    rng: random.Random,
    length: int = 10,
) -> str:
    return random_text(
        rng,
        string.ascii_lowercase
        + string.digits,
        length,
    )


def choose_positive_name(
    rng: random.Random,
) -> str:
    roll = rng.random()

    if roll < 0.20:
        return rng.choice(
            IDENTIFIER_NAMES
        )

    if roll < 0.55:
        return rng.choice(
            SECRET_NAMES
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
            rng.choice(
                (4, 5, 6)
            )
        )
    ]

    separator = rng.choice(
        (
            "-",
            ".",
            " ",
        )
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
            rng.choice(
                (4, 5)
            )
        )
    ]

    separator = rng.choice(
        (
            "-",
            " ",
        )
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
                11,
            ),
            random_base64url(
                rng,
                17,
            ),
            random_base64url(
                rng,
                15,
            ),
        )
    )


def generate_positive(
    index: int,
    rng: random.Random,
) -> dict:
    sample_type = POSITIVE_TYPES[
        index % len(
            POSITIVE_TYPES
        )
    ]

    variable_name = (
        choose_positive_name(
            rng
        )
    )

    if sample_type == (
        "alternate_random_secret"
    ):
        value = random_text(
            rng,
            (
                string.ascii_letters
                + string.digits
                + "_-!$%@"
            ),
            rng.choice(
                (
                    28,
                    34,
                    42,
                )
            ),
        )

    elif sample_type == (
        "alternate_passphrase_secret"
    ):
        value = generate_passphrase(
            rng
        )

    elif sample_type == (
        "alternate_jwt_secret"
    ):
        value = generate_jwt_like(
            rng
        )

    elif sample_type == (
        "alternate_hex_secret"
    ):
        value = random_hex(
            rng,
            rng.choice(
                (
                    32,
                    48,
                    64,
                )
            ),
        )

    elif sample_type == (
        "alternate_uuid_secret"
    ):
        value = random_uuid(
            rng
        )

    elif sample_type == (
        "alternate_base64_secret"
    ):
        value = random_base64url(
            rng,
            rng.choice(
                (
                    22,
                    26,
                    30,
                )
            ),
        )

    elif sample_type == (
        "alternate_client_exposed_secret"
    ):
        if rng.random() < 0.5:
            variable_name = rng.choice(
                (
                    "VITE_BACKEND_TOKEN",
                    "VITE_SERVICE_CREDENTIAL",
                    "VITE_PRIVATE_API_KEY",
                )
            )
        else:
            variable_name = rng.choice(
                (
                    "NEXT_PUBLIC_PRIVATE_TOKEN",
                    "NEXT_PUBLIC_BACKEND_KEY",
                    "NEXT_PUBLIC_SERVICE_SECRET",
                )
            )

        value = random_text(
            rng,
            (
                string.ascii_letters
                + string.digits
                + "_-"
            ),
            rng.choice(
                (
                    30,
                    36,
                    42,
                )
            ),
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
        "source": "candidate_v2_dev_v1",
    }


def generate_negative(
    index: int,
    rng: random.Random,
) -> dict:
    sample_type = NEGATIVE_TYPES[
        index % len(
            NEGATIVE_TYPES
        )
    ]

    tag = random_tag(
        rng
    )

    if sample_type == (
        "alternate_uuid_identifier"
    ):
        variable_name = rng.choice(
            SAFE_IDENTIFIER_NAMES
        )

        value = random_uuid(
            rng
        )

    elif sample_type == (
        "alternate_source_hash"
    ):
        variable_name = rng.choice(
            (
                "source_revision",
                "repository_hash",
                "commit_identifier",
            )
        )

        value = random_hex(
            rng,
            40,
        )

    elif sample_type == (
        "alternate_checksum"
    ):
        variable_name = rng.choice(
            (
                "package_checksum",
                "archive_digest",
                "content_checksum",
            )
        )

        value = random_hex(
            rng,
            64,
        )

    elif sample_type == (
        "alternate_secret_reference"
    ):
        variable_name = rng.choice(
            SECRET_NAMES
        )

        value = rng.choice(
            (
                f"${{SERVICE_CREDENTIAL_{tag.upper()}}}",
                f"$env:PRIVATE_TOKEN_{tag.upper()}",
                (
                    "process.env."
                    f"BACKEND_KEY_{tag.upper()}"
                ),
                (
                    "vault://team/service/"
                    f"{tag}"
                ),
            )
        )

    elif sample_type == (
        "alternate_placeholder"
    ):
        variable_name = rng.choice(
            SECRET_NAMES
        )

        value = rng.choice(
            (
                f"example-value-{tag}",
                f"replace-this-{tag}",
                f"demo-credential-{tag}",
                (
                    "YOUR_SECRET_HERE_"
                    f"{tag.upper()}"
                ),
            )
        )

    elif sample_type == (
        "alternate_documentation_jwt"
    ):
        variable_name = rng.choice(
            (
                "example_bearer",
                "documentation_jwt",
                "sample_token",
            )
        )

        value = generate_jwt_like(
            rng
        )

    elif sample_type == (
        "alternate_safe_phrase"
    ):
        variable_name = rng.choice(
            (
                "deployment_description",
                "runtime_policy",
                "feature_configuration",
            )
        )

        value = generate_safe_phrase(
            rng
        )

    elif sample_type == (
        "alternate_public_identifier"
    ):
        variable_name = rng.choice(
            (
                "external_reference",
                "public_resource_id",
                "operation_reference",
            )
        )

        value = random_text(
            rng,
            (
                string.ascii_uppercase
                + string.digits
            ),
            24,
        )

    elif sample_type == (
        "alternate_frontend_public_config"
    ):
        if rng.random() < 0.5:
            variable_name = rng.choice(
                (
                    "VITE_PUBLIC_REGION",
                    "VITE_RELEASE_CHANNEL",
                    "VITE_APP_MODE",
                )
            )
        else:
            variable_name = rng.choice(
                (
                    "NEXT_PUBLIC_REGION",
                    "NEXT_PUBLIC_RELEASE_CHANNEL",
                    "NEXT_PUBLIC_APP_MODE",
                )
            )

        base_value = rng.choice(
            (
                "stable",
                "preview",
                "eu-central",
                "public-dashboard",
                "production",
            )
        )

        value = (
            f"{base_value}-{tag}"
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
        "source": "candidate_v2_dev_v1",
    }


def add_features(
    sample: dict,
) -> dict:
    features = (
        extract_context_features(
            variable_name=sample[
                "variable_name"
            ],
            value=sample[
                "value"
            ],
        )
    )

    return {
        **sample,
        **features,
    }


def generate_unique_sample(
    generator,
    index: int,
    rng: random.Random,
    seen_candidates: set,
) -> dict:
    for _ in range(100):
        sample = generator(
            index=index,
            rng=rng,
        )

        candidate = (
            sample["variable_name"],
            sample["value"],
        )

        if candidate not in (
            seen_candidates
        ):
            seen_candidates.add(
                candidate
            )

            return add_features(
                sample
            )

    raise RuntimeError(
        "Unable to generate a unique "
        "development candidate."
    )


def generate_candidate_v2_devset(
    samples_per_class: int = (
        DEFAULT_SAMPLES_PER_CLASS
    ),
    seed: int = DEVSET_SEED,
) -> pd.DataFrame:
    if samples_per_class <= 0:
        raise ValueError(
            "samples_per_class must "
            "be greater than zero."
        )

    rng = random.Random(
        seed
    )

    seen_candidates = set()
    records = []

    for index in range(
        samples_per_class
    ):
        records.append(
            generate_unique_sample(
                generator=generate_positive,
                index=index,
                rng=rng,
                seen_candidates=(
                    seen_candidates
                ),
            )
        )

        records.append(
            generate_unique_sample(
                generator=generate_negative,
                index=index,
                rng=rng,
                seen_candidates=(
                    seen_candidates
                ),
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
            f"LG-CV2-DEV-{index:06d}"
            for index in range(
                1,
                len(dataframe) + 1,
            )
        ],
    )

    return dataframe


def save_candidate_v2_devset(
    output_path: Path,
    samples_per_class: int = (
        DEFAULT_SAMPLES_PER_CLASS
    ),
    seed: int = DEVSET_SEED,
) -> pd.DataFrame:
    dataframe = (
        generate_candidate_v2_devset(
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
