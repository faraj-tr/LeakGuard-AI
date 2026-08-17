from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


def test_benchmark_reports_are_explicitly_ignored():
    ignore_file = (
        PROJECT_ROOT
        / ".leakguardignore"
    )

    lines = {
        line.strip()
        for line in ignore_file.read_text(
            encoding="utf-8-sig"
        ).splitlines()
        if line.strip()
        and not line.lstrip().startswith("#")
    }

    expected = {
        "reports/final_benchmark_v1.json",
        "reports/candidate_v2_holdout_benchmark_v1.json",
    }

    assert expected <= lines

    assert (
        "reports/final_benchmark_v1.json"
        "reports/candidate_v2_holdout_benchmark_v1.json"
        not in lines
    )
