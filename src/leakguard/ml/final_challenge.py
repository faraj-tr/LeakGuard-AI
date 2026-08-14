import base64
import random
import string
from pathlib import Path

import pandas as pd

from leakguard.ml.features import (
    extract_ml_features,
)


FINAL_CHALLENGE_SEED = 8142026
FINAL_SAMPLES_PER_CLASS = 300


POSITIVE_TYPES = (
    "prefixed_opaque_secret",
    "colon_segment_secret",
    "credential_uri_secret",
    "word_chain_secret",
    "base32_secret",
    "compact_mixed_secret",
)


NEGATIVE_TYPES = (
    "ulid_identifier",
    "sri_integrity",
    "http_etag",
    "telemetry_span",
    "deployment_revision",
    "public_webhook_id",
    "config_template_reference",
    "documentation_literal",
    "astro_public_config",
    "certificate_fingerprint",
)


NEUTRAL_SECRET_NAMES = (
    "runtime_material",
    "opaque_setting",
    "bootstrap_value",
    "handshake_data",
    "connector_value",
    "session_blob",
    "transport_value",
    "deployment_material",
)


SENSITIVE_SECRET_NAMES = (
    "signing_secret",
    "machine_token",
    "service_password",
    "private_credential",
)


WORD_POOL = (
    "forest",
    "silver",
    "orbit",
    "falcon",
    "river",
    "marble",
    "planet",
    "garden",
    "signal",
    "winter",
    "bridge",
    "ocean",
    "violet",
    "rocket",
    "temple",
    "shadow",
    "copper",
    "harvest",
    "summit",
    "prairie",
)


CROCKFORD_ALPHABET = (
    "0123456789"
    "ABCDEFGHJKMNPQRSTVWXYZ"
)


def random_text(
    rng: random.Random,
    alphabet: str,
    length: int,
) -> str:
    """
    Generate deterministic random text.
    """

    return "".join(
        rng.choice(alphabet)
        for _ in range(length)
    )


def random_bytes(
    rng: random.Random,
    length: int,
) -> bytes:
    """
    Generate deterministic random bytes.
    """

    return bytes(
        rng.randrange(
            0,
            256,
        )
        for _ in range(length)
    )


def random_hex(
    rng: random.Random,
    length: int,
) -> str:
    """
    Generate deterministic hexadecimal text.
    """

    return random_text(
        rng=rng,
        alphabet=(
            string.digits
            + "abcdef"
        ),
        length=length,
    )


def random_base64(
    rng: random.Random,
    byte_length: int,
) -> str:
    """
    Generate deterministic Base64 text.
    """

    return (
        base64.b64encode(
            random_bytes(
                rng,
                byte_length,
            )
        )
        .decode("ascii")
    )


def random_base32(
    rng: random.Random,
    byte_length: int,
) -> str:
    """
    Generate deterministic Base32 text.
    """

    return (
        base64.b32encode(
            random_bytes(
                rng,
                byte_length,
            )
        )
        .decode("ascii")
        .rstrip("=")
    )


def choose_secret_name(
    index: int,
    rng: random.Random,
) -> str:
    """
    Use mostly neutral variable names.

    Only one out of every five secrets
    receives an obviously sensitive name.
    """

    if index % 5 == 0:

        return rng.choice(
            SENSITIVE_SECRET_NAMES
        )

    return rng.choice(
        NEUTRAL_SECRET_NAMES
    )


def generate_positive_value(
    sample_type: str,
    rng: random.Random,
) -> str:
    """
    Generate a secret using structures
    not used by the previous challenge
    generator.
    """

    if sample_type == (
        "prefixed_opaque_secret"
    ):

        prefix = rng.choice(
            (
                "qx_",
                "svc1_",
                "mx_",
                "rtk_",
            )
        )

        body = random_text(
            rng=rng,
            alphabet=(
                string.ascii_letters
                + string.digits
                + "_-"
            ),
            length=40,
        )

        return prefix + body

    if sample_type == (
        "colon_segment_secret"
    ):

        segments = [
            random_text(
                rng=rng,
                alphabet=(
                    string.ascii_letters
                    + string.digits
                ),
                length=8,
            )
            for _ in range(4)
        ]

        return ":".join(
            segments
        )

    if sample_type == (
        "credential_uri_secret"
    ):

        generated_credential = random_text(
            rng=rng,
            alphabet=(
                string.ascii_letters
                + string.digits
                + "_-"
            ),
            length=22,
        )

        scheme = rng.choice(
            (
                "redis",
                "postgresql",
                "mongodb",
            )
        )

        return (
            f"{scheme}://worker:"
            f"{generated_credential}"
            "@internal.service.local/"
            "application"
        )

    if sample_type == (
        "word_chain_secret"
    ):

        words = [
            rng.choice(
                WORD_POOL
            )
            for _ in range(6)
        ]

        return ".".join(
            words
        )

    if sample_type == (
        "base32_secret"
    ):

        return random_base32(
            rng=rng,
            byte_length=28,
        )

    if sample_type == (
        "compact_mixed_secret"
    ):

        return random_text(
            rng=rng,
            alphabet=(
                string.ascii_letters
                + string.digits
                + "!#$%_-"
            ),
            length=30,
        )

    raise ValueError(
        "Unsupported final secret type: "
        f"{sample_type}"
    )


def generate_positive_sample(
    index: int,
    rng: random.Random,
) -> dict:
    """
    Generate one final challenge secret.
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
        choose_secret_name(
            index=index,
            rng=rng,
        )
    )

    value = (
        generate_positive_value(
            sample_type=sample_type,
            rng=rng,
        )
    )

    return {
        "variable_name": variable_name,
        "value": value,
        "label": 1,
        "sample_type": sample_type,
        "framework": "none",
        "source": "final_challenge_v2",
    }


def generate_negative_sample(
    index: int,
    rng: random.Random,
) -> dict:
    """
    Generate one safe final challenge
    sample.

    Several safe types intentionally have
    high entropy or sensitive-looking names.
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

    if sample_type == "ulid_identifier":

        variable_name = "event_ulid"

        value = random_text(
            rng=rng,
            alphabet=(
                CROCKFORD_ALPHABET
            ),
            length=26,
        )

    elif sample_type == "sri_integrity":

        variable_name = (
            "script_integrity"
        )

        value = (
            "sha384-"
            + random_base64(
                rng=rng,
                byte_length=36,
            )
        )

    elif sample_type == "http_etag":

        variable_name = "response_etag"

        value = (
            '"'
            + random_hex(
                rng=rng,
                length=32,
            )
            + '"'
        )

    elif sample_type == "telemetry_span":

        variable_name = "span_identifier"

        value = random_hex(
            rng=rng,
            length=32,
        )

    elif sample_type == (
        "deployment_revision"
    ):

        variable_name = (
            "deployment_revision"
        )

        value = (
            "rev-"
            + random_hex(
                rng=rng,
                length=18,
            )
            + "-"
            + str(
                1000 + index
            )
        )

    elif sample_type == (
        "public_webhook_id"
    ):

        variable_name = (
            "public_webhook_id"
        )

        value = (
            "whpub_"
            + random_text(
                rng=rng,
                alphabet=(
                    string.ascii_letters
                    + string.digits
                ),
                length=30,
            )
        )

    elif sample_type == (
        "config_template_reference"
    ):

        variable_name = rng.choice(
            (
                "api_key_template",
                "password_template",
                "secret_template",
                "token_template",
            )
        )

        value = (
            "{{ vault.reference."
            + str(index)
            + " }}"
        )

    elif sample_type == (
        "documentation_literal"
    ):

        variable_name = rng.choice(
            (
                "credential_example",
                "secret_example",
                "token_example",
                "password_example",
            )
        )

        value = (
            "EXAMPLE_ONLY_NOT_A_SECRET_"
            + str(index)
        )

    elif sample_type == (
        "astro_public_config"
    ):

        framework = "Astro"

        variable_name = rng.choice(
            (
                "PUBLIC_SITE_CHANNEL",
                "PUBLIC_DOCS_VERSION",
                "PUBLIC_ASSET_HOST",
            )
        )

        value = (
            "public-value-"
            + str(index)
        )

    elif sample_type == (
        "certificate_fingerprint"
    ):

        variable_name = (
            "certificate_fingerprint"
        )

        segments = [
            random_hex(
                rng=rng,
                length=2,
            ).upper()
            for _ in range(20)
        ]

        value = ":".join(
            segments
        )

    else:

        raise ValueError(
            "Unsupported final safe type: "
            f"{sample_type}"
        )

    return {
        "variable_name": variable_name,
        "value": value,
        "label": 0,
        "sample_type": sample_type,
        "framework": framework,
        "source": "final_challenge_v2",
    }


def add_features(
    sample: dict,
) -> dict:
    """
    Add the same numerical features used
    by the existing LeakGuard models.
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


def generate_final_challenge_dataset(
    samples_per_class: int = (
        FINAL_SAMPLES_PER_CLASS
    ),
    seed: int = FINAL_CHALLENGE_SEED,
) -> pd.DataFrame:
    """
    Generate Final Challenge Dataset v2.

    This dataset must never be used for
    training, weight tuning, threshold
    tuning, or feature selection.
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
            f"LGF2-{index:06d}"
            for index in range(
                1,
                len(dataframe) + 1,
            )
        ],
    )

    return dataframe


def save_final_challenge_dataset(
    output_path: Path,
    samples_per_class: int = (
        FINAL_SAMPLES_PER_CLASS
    ),
    seed: int = FINAL_CHALLENGE_SEED,
) -> pd.DataFrame:
    """
    Generate and save Final Challenge v2.
    """

    dataframe = (
        generate_final_challenge_dataset(
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