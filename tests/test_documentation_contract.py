from pathlib import Path
import tomllib

from leakguard.artifacts import (
    ARTIFACT_DIRECTORIES,
    ARTIFACT_EXTENSIONS,
)
from leakguard.config import (
    SUPPORTED_ML_MODE,
)
from leakguard.ml.candidate_v2_distribution import (
    CANDIDATE_V2_ARTIFACT_FILENAME,
    EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256,
)
from leakguard.ml.candidate_v2_holdout_gate import (
    EXPECTED_HOLDOUT_SHA256,
)
from leakguard.ml.candidate_v2_locked import (
    LOCKED_CONTEXT_WEIGHT,
    LOCKED_TEXT_WEIGHT,
    LOCKED_THRESHOLD,
)
from leakguard.ml.fresh_dev_gate import (
    EXPECTED_DEVELOPMENT_SHA256,
    EXPECTED_TRAINING_SHA256,
)
from leakguard.runtime import (
    API_HOST,
    API_PORT,
    UI_HOST,
    UI_PORT,
)
from leakguard.scan_safety import (
    MAX_SCANNABLE_FILE_BYTES,
)
from leakguard.scanner import (
    SKIP_DIRECTORIES,
    SPECIAL_FILES,
    SUPPORTED_EXTENSIONS,
)
from leakguard.version import __version__


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

README_PATH = PROJECT_ROOT / "README.md"
SECURITY_PATH = PROJECT_ROOT / "SECURITY.md"
DOCS_ROOT = PROJECT_ROOT / "docs"

REQUIRED_DOCS = {
    "README.md": README_PATH,
    "SECURITY.md": SECURITY_PATH,
    "docs/README.md": DOCS_ROOT / "README.md",
    "docs/architecture.md": (
        DOCS_ROOT / "architecture.md"
    ),
    "docs/security-model.md": (
        DOCS_ROOT / "security-model.md"
    ),
    "docs/threat-model.md": (
        DOCS_ROOT / "threat-model.md"
    ),
    "docs/model-card-candidate-v2.md": (
        DOCS_ROOT
        / "model-card-candidate-v2.md"
    ),
    "docs/data-card.md": (
        DOCS_ROOT / "data-card.md"
    ),
    "docs/model-development-guide.md": (
        DOCS_ROOT
        / "model-development-guide.md"
    ),
}


def read_text(path: Path) -> str:
    return path.read_text(
        encoding="utf-8-sig"
    )


def test_required_documentation_exists():
    missing = [
        name
        for name, path in REQUIRED_DOCS.items()
        if not path.is_file()
    ]

    assert not missing, (
        "Missing required documentation: "
        + ", ".join(missing)
    )


def test_readme_version_matches_runtime_version():
    readme = read_text(README_PATH)

    assert (
        f"| Version | `{__version__}` |"
        in readme
    )


def test_readme_python_requirement_matches_pyproject():
    pyproject_path = (
        PROJECT_ROOT
        / "pyproject.toml"
    )

    with pyproject_path.open(
        "rb"
    ) as handle:
        pyproject = tomllib.load(handle)

    requirement = pyproject[
        "project"
    ][
        "requires-python"
    ]

    readme = read_text(README_PATH)

    assert (
        f"| Python | `{requirement}` |"
        in readme
    )


def test_readme_documents_console_entrypoints():
    pyproject_path = (
        PROJECT_ROOT
        / "pyproject.toml"
    )

    with pyproject_path.open(
        "rb"
    ) as handle:
        pyproject = tomllib.load(handle)

    scripts = set(
        pyproject[
            "project"
        ][
            "scripts"
        ]
    )

    readme = read_text(README_PATH)

    for script in sorted(scripts):
        assert script in readme


def test_readme_documents_runtime_bindings():
    readme = read_text(README_PATH)

    assert (
        f"{API_HOST}:{API_PORT}"
        in readme
    )

    assert (
        f"{UI_HOST}:{UI_PORT}"
        in readme
    )


def test_documentation_preserves_advisory_only_ml():
    readme = read_text(README_PATH)
    architecture = read_text(
        DOCS_ROOT / "architecture.md"
    )
    security_model = read_text(
        DOCS_ROOT / "security-model.md"
    )

    assert SUPPORTED_ML_MODE == "advisory"

    combined = (
        readme
        + architecture
        + security_model
    ).lower()

    assert "advisory only" in combined
    assert "blocking = false" in combined
    assert "calibrated = false" in combined


def test_documentation_matches_scan_size_limit():
    assert (
        MAX_SCANNABLE_FILE_BYTES
        == 2 * 1024 * 1024
    )

    readme = read_text(README_PATH)
    architecture = read_text(
        DOCS_ROOT / "architecture.md"
    )

    assert "2 MiB" in readme
    assert "2 MiB" in architecture


def test_architecture_documents_source_scope():
    architecture = read_text(
        DOCS_ROOT / "architecture.md"
    )

    for extension in sorted(
        SUPPORTED_EXTENSIONS
    ):
        assert extension in architecture

    for filename in sorted(
        SPECIAL_FILES
    ):
        assert filename in architecture

    for directory in sorted(
        SKIP_DIRECTORIES
    ):
        assert directory in architecture


def test_documentation_matches_artifact_scope():
    readme = read_text(README_PATH)
    architecture = read_text(
        DOCS_ROOT / "architecture.md"
    )

    combined = readme + architecture

    for path in ARTIFACT_DIRECTORIES:
        assert (
            path.as_posix()
            in combined
        )

    for extension in sorted(
        ARTIFACT_EXTENSIONS
    ):
        assert extension in combined


def test_model_card_matches_locked_configuration():
    model_card = read_text(
        DOCS_ROOT
        / "model-card-candidate-v2.md"
    )

    assert (
        f"| Text weight | `{LOCKED_TEXT_WEIGHT:.2f}` |"
        in model_card
    )

    assert (
        f"| Context weight | `{LOCKED_CONTEXT_WEIGHT:.2f}` |"
        in model_card
    )

    assert (
        f"| Threshold | `{LOCKED_THRESHOLD:.2f}` |"
        in model_card
    )


def test_model_docs_match_dataset_identities():
    model_card = read_text(
        DOCS_ROOT
        / "model-card-candidate-v2.md"
    )
    data_card = read_text(
        DOCS_ROOT / "data-card.md"
    )
    guide = read_text(
        DOCS_ROOT
        / "model-development-guide.md"
    )

    combined = (
        model_card
        + data_card
        + guide
    )

    for digest in (
        EXPECTED_TRAINING_SHA256,
        EXPECTED_DEVELOPMENT_SHA256,
        EXPECTED_HOLDOUT_SHA256,
    ):
        assert digest in combined


def test_model_docs_match_trusted_artifact_identity():
    model_card = read_text(
        DOCS_ROOT
        / "model-card-candidate-v2.md"
    )
    guide = read_text(
        DOCS_ROOT
        / "model-development-guide.md"
    )

    combined = (
        model_card
        + guide
    )

    assert (
        CANDIDATE_V2_ARTIFACT_FILENAME
        in combined
    )

    assert (
        EXPECTED_CANDIDATE_V2_ARTIFACT_SHA256
        in combined
    )


def test_readme_links_all_security_documents():
    readme = read_text(README_PATH)

    expected_links = (
        "docs/README.md",
        "docs/architecture.md",
        "docs/security-model.md",
        "docs/threat-model.md",
        "docs/model-development-guide.md",
        "docs/model-card-candidate-v2.md",
        "docs/data-card.md",
        "SECURITY.md",
    )

    for link in expected_links:
        assert link in readme


def test_security_policy_uses_safe_reporting_language():
    security = read_text(
        SECURITY_PATH
    ).lower()

    assert (
        "do not include real active credentials"
        in security
    )

    assert "synthetic" in security

    assert (
        "live credential" in security
        or "live credentials" in security
    )
