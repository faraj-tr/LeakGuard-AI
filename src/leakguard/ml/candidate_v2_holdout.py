import base64
import random
import string
import uuid
from pathlib import Path

import pandas as pd

from leakguard.ml.candidate_v2_metadata import (
    looks_like_safe_hash_metadata,
)
from leakguard.ml.context_features import (
    extract_context_features,
)


HOLDOUT_SEED = 8152601
DEFAULT_SAMPLES_PER_CLASS = 400

HOLDOUT_SOURCE = (
    "candidate_v2_"
    + "holdout_v1"
)


POSITIVE_TYPES = (
    "holdout_rotating_access_secret",
    "holdout_bearer_triplet_secret",
    "holdout_standard_base64_secret",
    "holdout_uuid_credential_secret",
    "holdout_segmented_secret",
    "holdout_client_runtime_secret",
    "holdout_hex_material_secret",
    "holdout_misleading_hash_secret",
    "holdout_phrase_credential_secret",
)


NEGATIVE_TYPES = (
    "holdout_release_commit_hash",
    "holdout_module_checksum_hash",
    "holdout_documentation_bearer",
    "holdout_secret_store_reference",
    "holdout_redacted_configuration",
    "holdout_frontend_public_setting",
    "holdout_object_uuid_identifier",
    "holdout_public_segmented_identifier",
    "holdout_safe_configuration_phrase",
    "holdout_public_base64_blob",
)


SENSITIVE_NAMES = (
    "access_token",
    "client_secret",
    "service_password",
    "api_secret",
    "auth_token",
    "private_key",
)


NEUTRAL_NAMES = (
    "runtime_material",
    "application_data",
    "connector_material",
    "opaque_value",
    "session_material",
    "integration_value",
)


SECRET_IDENTIFIER_NAMES = (
    "credential_id",
    "auth_reference",
    "private_identifier",
    "session_reference",
)


SECRET_PHRASE_WORDS = (
    "atlas",
    "birch",
    "cobalt",
    "drift",
    "eagle",
    "frost",
    "glacier",
    "helium",
    "iris",
    "jade",
    "keystone",
    "lotus",
    "matrix",
    "north",
    "opal",
    "pine",
    "raven",
    "stone",
    "tundra",
)


SAFE_PHRASE_WORDS = (
    "application",
    "deployment",
    "feature",
    "public",
    "region",
    "release",
    "runtime",
    "service",
    "stable",
    "staging",
    "default",
    "enabled",
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
        "0123456789abcdef",
        length,
    )


def random_uuid(
    rng: random.Random,
) -> str:
    return str(
        uuid.UUID(
            int=rng.getrandbits(128)
        )
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


def random_standard_base64(
    rng: random.Random,
    byte_length: int,
) -> str:
    raw = bytes(
        rng.randrange(0, 256)
        for _ in range(byte_length)
    )

    return base64.b64encode(
        raw
    ).decode("ascii")


def random_tag(
    rng: random.Random,
    length: int = 9,
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

    if roll < 0.18:
        return rng.choice(
            SECRET_IDENTIFIER_NAMES
        )

    if roll < 0.55:
        return rng.choice(
            SENSITIVE_NAMES
        )

    return rng.choice(
        NEUTRAL_NAMES
    )


def generate_bearer_triplet(
    rng: random.Random,
) -> str:
    return ".".join(
        (
            random_base64url(
                rng,
                13,
            ),
            random_base64url(
                rng,
                19,
            ),
            random_base64url(
                rng,
                17,
            ),
        )
    )


def generate_secret_phrase(
    rng: random.Random,
) -> str:
    words = [
        rng.choice(
            SECRET_PHRASE_WORDS
        )
        for _ in range(
            rng.choice(
                (4, 5, 6)
            )
        )
    ]

    separator = rng.choice(
        (
            " ",
            "-",
            ".",
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
            " ",
            "-",
        )
    )

    return separator.join(
        words
    )


def generate_segmented_value(
    rng: random.Random,
) -> str:
    alphabet = (
        string.ascii_letters
        + string.digits
    )

    groups = [
        random_text(
            rng,
            alphabet,
            6,
        )
        for _ in range(5)
    ]

    return "-".join(
        groups
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
        "holdout_rotating_access_secret"
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
                    31,
                    37,
                    45,
                )
            ),
        )

    elif sample_type == (
        "holdout_bearer_triplet_secret"
    ):
        value = generate_bearer_triplet(
            rng
        )

    elif sample_type == (
        "holdout_standard_base64_secret"
    ):
        value = random_standard_base64(
            rng,
            rng.choice(
                (
                    23,
                    27,
                    31,
                )
            ),
        )

    elif sample_type == (
        "holdout_uuid_credential_secret"
    ):
        value = random_uuid(
            rng
        )

    elif sample_type == (
        "holdout_segmented_secret"
    ):
        value = generate_segmented_value(
            rng
        )

    elif sample_type == (
        "holdout_client_runtime_secret"
    ):
        if rng.random() < 0.5:
            variable_name = rng.choice(
                (
                    "VITE_AUTH_TOKEN",
                    "VITE_PRIVATE_KEY",
                    "VITE_SERVICE_SECRET",
                )
            )
        else:
            variable_name = rng.choice(
                (
                    "NEXT_PUBLIC_AUTH_TOKEN",
                    "NEXT_PUBLIC_PRIVATE_KEY",
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
                    33,
                    39,
                    45,
                )
            ),
        )

    elif sample_type == (
        "holdout_hex_material_secret"
    ):
        value = random_hex(
            rng,
            rng.choice(
                (
                    40,
                    64,
                )
            ),
        )

    elif sample_type == (
        "holdout_misleading_hash_secret"
    ):
        variable_name = rng.choice(
            (
                "repository_revision",
                "source_fingerprint",
                "release_commit_sha",
                "module_checksum",
            )
        )

        value = random_hex(
            rng,
            rng.choice(
                (
                    40,
                    64,
                )
            ),
        )

    elif sample_type == (
        "holdout_phrase_credential_secret"
    ):
        value = generate_secret_phrase(
            rng
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
        "source": HOLDOUT_SOURCE,
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
        "holdout_release_commit_hash"
    ):
        variable_name = rng.choice(
            (
                "release_commit_sha",
                "repository_revision",
                "source_commit",
            )
        )

        value = random_hex(
            rng,
            40,
        )

    elif sample_type == (
        "holdout_module_checksum_hash"
    ):
        variable_name = rng.choice(
            (
                "module_checksum",
                "package_digest",
                "source_fingerprint",
            )
        )

        value = random_hex(
            rng,
            64,
        )

    elif sample_type == (
        "holdout_documentation_bearer"
    ):
        variable_name = rng.choice(
            (
                "documentation_bearer",
                "example_access_value",
                "sample_auth_value",
            )
        )

        value = generate_bearer_triplet(
            rng
        )

    elif sample_type == (
        "holdout_secret_store_reference"
    ):
        variable_name = rng.choice(
            SENSITIVE_NAMES
        )

        value = rng.choice(
            (
                (
                    "${PRIVATE_KEY_"
                    f"{tag.upper()}}}"
                ),
                (
                    "$env:AUTH_TOKEN_"
                    f"{tag.upper()}"
                ),
                (
                    "process.env."
                    f"SERVICE_PASSWORD_{tag.upper()}"
                ),
                (
                    "vault://security/runtime/"
                    f"{tag}"
                ),
                (
                    "%CLIENT_SECRET_"
                    f"{tag.upper()}%"
                ),
            )
        )

    elif sample_type == (
        "holdout_redacted_configuration"
    ):
        variable_name = rng.choice(
            SENSITIVE_NAMES
        )

        value = rng.choice(
            (
                f"replace-this-{tag}",
                f"example-secret-{tag}",
                f"demo-only-{tag}",
                (
                    "YOUR_CREDENTIAL_HERE_"
                    f"{tag.upper()}"
                ),
                f"<redacted-{tag}>",
            )
        )

    elif sample_type == (
        "holdout_frontend_public_setting"
    ):
        if rng.random() < 0.5:
            variable_name = rng.choice(
                (
                    "VITE_PUBLIC_LOCALE",
                    "VITE_RELEASE_MODE",
                    "VITE_PUBLIC_REGION",
                )
            )
        else:
            variable_name = rng.choice(
                (
                    "NEXT_PUBLIC_LOCALE",
                    "NEXT_PUBLIC_RELEASE_MODE",
                    "NEXT_PUBLIC_REGION",
                )
            )

        value = (
            rng.choice(
                (
                    "stable",
                    "preview",
                    "eu-north",
                    "public-ui",
                )
            )
            + "-"
            + tag
        )

    elif sample_type == (
        "holdout_object_uuid_identifier"
    ):
        variable_name = rng.choice(
            (
                "object_id",
                "resource_uuid",
                "operation_identifier",
            )
        )

        value = random_uuid(
            rng
        )

    elif sample_type == (
        "holdout_public_segmented_identifier"
    ):
        variable_name = rng.choice(
            (
                "public_reference",
                "license_identifier",
                "tracking_id",
            )
        )

        value = generate_segmented_value(
            rng
        )

    elif sample_type == (
        "holdout_safe_configuration_phrase"
    ):
        variable_name = rng.choice(
            (
                "deployment_policy",
                "runtime_description",
                "service_configuration",
            )
        )

        value = generate_safe_phrase(
            rng
        )

    elif sample_type == (
        "holdout_public_base64_blob"
    ):
        variable_name = rng.choice(
            (
                "public_asset_blob",
                "resource_blob",
                "icon_payload",
            )
        )

        value = random_standard_base64(
            rng,
            rng.choice(
                (
                    23,
                    27,
                    31,
                )
            ),
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
        "source": HOLDOUT_SOURCE,
    }


def add_features(
    sample: dict,
) -> dict:
    context = extract_context_features(
        variable_name=sample[
            "variable_name"
        ],
        value=sample[
            "value"
        ],
    )

    context[
        "looks_like_safe_hash_metadata"
    ] = looks_like_safe_hash_metadata(
        variable_name=sample[
            "variable_name"
        ],
        value=sample[
            "value"
        ],
    )

    return {
        **sample,
        **context,
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
        "holdout candidate."
    )


def generate_candidate_v2_holdout(
    samples_per_class: int = (
        DEFAULT_SAMPLES_PER_CLASS
    ),
    seed: int = HOLDOUT_SEED,
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
            f"LG-CV2-HOLD-{index:06d}"
            for index in range(
                1,
                len(dataframe) + 1,
            )
        ],
    )

    return dataframe


def save_candidate_v2_holdout(
    output_path: Path,
    samples_per_class: int = (
        DEFAULT_SAMPLES_PER_CLASS
    ),
    seed: int = HOLDOUT_SEED,
) -> pd.DataFrame:
    dataframe = (
        generate_candidate_v2_holdout(
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



