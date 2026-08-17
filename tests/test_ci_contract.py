from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

WORKFLOW_ROOT = (
    PROJECT_ROOT
    / ".github"
    / "workflows"
)


def read_workflow(
    filename,
):
    return (
        WORKFLOW_ROOT
        / filename
    ).read_text(
        encoding="utf-8"
    )


def test_security_workflow_is_deterministic_gate():
    text = read_workflow(
        "leakguard-security.yml"
    )

    assert (
        "actions/checkout@v7"
        in text
    )

    assert (
        "actions/setup-python@v7"
        in text
    )

    assert (
        "leakguard scan . --no-ml-advisory"
        in text
    )

    assert "pytest" not in text


def test_security_workflow_uses_least_git_permissions():
    text = read_workflow(
        "leakguard-security.yml"
    )

    assert "contents: read" in text

    assert (
        "persist-credentials: false"
        in text
    )


def test_productization_ci_covers_supported_platforms():
    text = read_workflow(
        "productization-ci.yml"
    )

    required = {
        "ubuntu-latest",
        "windows-latest",
        "macos-latest",
        'python-version: "3.11"',
        'python-version: "3.12"',
    }

    assert all(
        item in text
        for item in required
    )


def test_productization_ci_builds_real_distribution():
    text = read_workflow(
        "productization-ci.yml"
    )

    assert (
        "python -m build"
        in text
    )

    assert "*.whl" in text
    assert "*.tar.gz" in text

    assert (
        "python -m venv .wheel-venv"
        in text
    )

    assert (
        "DISTRIBUTION_METADATA_OK"
        in text
    )

    assert (
        "CONSOLE_ENTRYPOINTS_OK"
        in text
    )


def test_productization_ci_uses_official_docker_build_actions():
    text = read_workflow(
        "productization-ci.yml"
    )

    assert (
        "docker/setup-buildx-action@v4"
        in text
    )

    assert (
        "docker/build-push-action@v7"
        in text
    )

    assert "push: false" in text
    assert "load: true" in text


def test_container_ci_preserves_runtime_hardening():
    text = read_workflow(
        "productization-ci.yml"
    )

    assert (
        "--security-opt no-new-privileges"
        in text
    )

    assert "--cap-drop ALL" in text

    assert (
        "target=/workspace,readonly"
        in text
    )

    assert (
        "target=/models,readonly"
        in text
    )


def test_container_ci_verifies_api_and_dashboard():
    text = read_workflow(
        "productization-ci.yml"
    )

    assert (
        ".State.Health.Status"
        in text
    )

    assert (
        "http://127.0.0.1:8501"
        in text
    )

    assert (
        "docker logs leakguard-ci"
        in text
    )

    assert (
        "docker rm -f leakguard-ci"
        in text
    )


def test_container_ci_prepares_safe_workspace_fixture():
    text = read_workflow(
        "productization-ci.yml"
    )

    assert (
        """echo 'message = "safe"'"""
        in text
    )
