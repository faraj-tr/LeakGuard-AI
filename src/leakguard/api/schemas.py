from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class HealthResponse(BaseModel):
    """
    Stable health contract for API clients.
    """

    status: Literal["ok"]
    service: Literal["leakguard-ai"]
    api_version: Literal["v1"]
    service_version: str


class ScanRequest(BaseModel):
    """
    Local project scan request.

    Unknown fields are rejected so HTTP
    clients cannot invent unsupported security
    controls such as ML blocking authority.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    path: str = Field(
        min_length=1
    )

    staged: bool = False

    ml_advisory: bool | None = None


class MLAdvisoryResponse(BaseModel):
    """
    Candidate v2 advisory metadata.

    Candidate v2 remains experimental and
    explicitly non-blocking.
    """

    available: bool
    model: str
    mode: Literal["advisory"]
    risk_score: float
    threshold: float

    prediction: Literal[
        "suspicious",
        "lower_risk",
    ]

    calibrated: Literal[False]
    blocking: Literal[False]


class FindingResponse(BaseModel):
    """
    Public secret-safe finding contract.
    """

    file: str
    line: int
    type: str

    severity: Literal[
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
    ]

    masked_value: str

    candidate_score: int | None
    framework: str | None

    reasons: list[str]

    ml_advisory: (
        MLAdvisoryResponse
        | None
    ) = None


class SeverityCounts(BaseModel):
    critical: int
    high: int
    medium: int
    low: int


class ScanResponse(BaseModel):
    """
    Structured security-gate result.
    """

    mode: Literal[
        "project",
        "staged",
    ]

    files_scanned: int
    findings_count: int

    gate: Literal[
        "passed",
        "failed",
    ]

    ml_advisory_enabled: bool

    severity_counts: SeverityCounts

    findings: list[
        FindingResponse
    ]


ErrorCode = Literal[
    "invalid_request",
    "path_outside_scan_root",
    "project_not_found",
    "invalid_project_path",
    "invalid_configuration",
    "scan_execution_failed",
    "internal_error",
]


class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str


class ErrorResponse(BaseModel):
    """
    Stable API error envelope.

    Internal exceptions, request bodies, and
    host filesystem details are intentionally
    excluded.
    """

    error: ErrorDetail
