from pathlib import Path

from leakguard.artifacts import (
    collect_dotenv_secret_inventory,
    discover_artifact_files,
    scan_artifact_content,
    scan_artifacts,
)


def test_discovers_supported_build_artifacts(
    tmp_path,
):
    dist_file = (
        tmp_path
        / "dist"
        / "assets"
        / "app.js"
    )

    build_file = (
        tmp_path
        / "build"
        / "index.html"
    )

    next_file = (
        tmp_path
        / ".next"
        / "static"
        / "chunk.js"
    )

    ignored_binary = (
        tmp_path
        / "dist"
        / "logo.png"
    )

    source_file = (
        tmp_path
        / "src"
        / "app.js"
    )

    for path in (
        dist_file,
        build_file,
        next_file,
        ignored_binary,
        source_file,
    ):
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            b"test"
        )

    discovered = (
        discover_artifact_files(
            tmp_path
        )
    )

    relative_paths = [
        path.relative_to(
            tmp_path
        ).as_posix()
        for path in discovered
    ]

    assert relative_paths == [
        ".next/static/chunk.js",
        "build/index.html",
        "dist/assets/app.js",
    ]


def test_inventory_collects_secret_like_dotenv_values(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_KEY_ABC123"
    )

    env_file = (
        tmp_path
        / ".env"
    )

    env_file.write_text(
        (
            f"API_KEY={secret}\n"
            "APP_TITLE=LeakGuard\n"
        ),
        encoding="utf-8",
    )

    inventory, limitations = (
        collect_dotenv_secret_inventory(
            tmp_path
        )
    )

    assert limitations == []
    assert len(inventory) == 1

    item = inventory[0]

    assert item.variable_name == (
        "API_KEY"
    )

    assert item.source_file == (
        env_file
    )

    assert item.candidate_score >= 40

    # repr() must not leak the raw value.
    assert secret not in repr(
        inventory
    )


def test_detects_dotenv_secret_propagated_into_dist(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_KEY_ABC123"
    )

    env_file = (
        tmp_path
        / ".env"
    )

    env_file.write_text(
        f"API_KEY={secret}",
        encoding="utf-8",
    )

    artifact = (
        tmp_path
        / "dist"
        / "assets"
        / "index.js"
    )

    artifact.parent.mkdir(
        parents=True,
    )

    artifact.write_text(
        (
            'const config={key:"'
            f'{secret}'
            '"};'
        ),
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_artifacts(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert len(findings) == 1

    finding = findings[0]

    assert finding["type"] == (
        "Artifact Secret Exposure"
    )

    assert finding["severity"] == (
        "CRITICAL"
    )

    assert finding["file"] == str(
        artifact
    )

    assert finding["line"] == 1

    assert finding["framework"] == (
        "Artifact"
    )

    assert secret not in str(
        findings
    )

    assert "API_KEY" in str(
        finding[
            "reasons"
        ]
    )


def test_clean_artifact_does_not_trigger_propagation(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_KEY_ABC123"
    )

    (
        tmp_path
        / ".env"
    ).write_text(
        f"API_KEY={secret}",
        encoding="utf-8",
    )

    artifact = (
        tmp_path
        / "dist"
        / "app.js"
    )

    artifact.parent.mkdir(
        parents=True,
    )

    artifact.write_text(
        (
            'console.log("'
            'Hello from production'
            '");'
        ),
        encoding="utf-8",
    )

    files_scanned, findings = (
        scan_artifacts(
            tmp_path
        )
    )

    assert files_scanned == 1
    assert findings == []


def test_repeated_secret_in_same_artifact_is_reported_once(
    tmp_path,
):
    secret = (
        "LEAKGUARD_FAKE_KEY_ABC123"
    )

    (
        tmp_path
        / ".env"
    ).write_text(
        f"API_KEY={secret}",
        encoding="utf-8",
    )

    inventory, limitations = (
        collect_dotenv_secret_inventory(
            tmp_path
        )
    )

    assert limitations == []

    artifact = Path(
        "dist/app.js"
    )

    content = (
        f'const a="{secret}";'
        f'const b="{secret}";'
    )

    findings = (
        scan_artifact_content(
            path=artifact,
            content=content,
            inventory=inventory,
        )
    )

    assert len(findings) == 1

    assert secret not in str(
        findings
    )


def test_public_dotenv_value_is_not_added_to_inventory(
    tmp_path,
):
    (
        tmp_path
        / ".env"
    ).write_text(
        "APP_TITLE=LeakGuard",
        encoding="utf-8",
    )

    inventory, limitations = (
        collect_dotenv_secret_inventory(
            tmp_path
        )
    )

    assert limitations == []
    assert inventory == []
