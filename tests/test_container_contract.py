from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


def read_project_file(
    name,
):
    return (
        PROJECT_ROOT
        / name
    ).read_text(
        encoding="utf-8"
    )


def test_dockerignore_excludes_local_sensitive_material():
    text = read_project_file(
        ".dockerignore"
    )

    required = {
        ".git/",
        ".venv/",
        ".env",
        ".env.*",
        "models/",
        "data/",
        "reports/",
        "tests/",
        "*.egg-info/",
    }

    assert required.issubset(
        set(
            text.splitlines()
        )
    )


def test_dockerfile_copies_only_runtime_package_inputs():
    text = read_project_file(
        "Dockerfile"
    )

    assert (
        "FROM python:3.12-slim"
        in text
    )

    assert (
        "COPY pyproject.toml ./"
        in text
    )

    assert (
        "COPY src ./src"
        in text
    )

    assert "COPY . ." not in text


def test_dockerfile_runs_as_non_root_user():
    text = read_project_file(
        "Dockerfile"
    )

    assert (
        "USER leakguard"
        in text
    )


def test_dockerfile_exposes_only_dashboard_port():
    text = read_project_file(
        "Dockerfile"
    )

    assert "EXPOSE 8501" in text
    assert "EXPOSE 8000" not in text

    assert (
        'CMD ["leakguard-stack"]'
        in text
    )


def test_dockerfile_healthcheck_targets_internal_api():
    text = read_project_file(
        "Dockerfile"
    )

    assert "HEALTHCHECK" in text

    assert (
        "http://127.0.0.1:8000/health"
        in text
    )


def test_compose_publishes_only_loopback_dashboard():
    text = read_project_file(
        "compose.yaml"
    )

    assert (
        '"127.0.0.1:8501:8501"'
        in text
    )

    assert (
        "8000:8000"
        not in text
    )


def test_compose_mounts_security_inputs_read_only():
    text = read_project_file(
        "compose.yaml"
    )

    assert (
        "target: /workspace"
        in text
    )

    assert (
        "target: /models"
        in text
    )

    assert (
        text.count(
            "read_only: true"
        )
        == 2
    )

    assert (
        "no-new-privileges:true"
        in text
    )

    assert (
        "cap_drop:"
        in text
    )

    assert (
        "- ALL"
        in text
    )
