from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """
    Stable health contract for API clients.

    This endpoint intentionally exposes no
    filesystem, model-path, or secret data.
    """

    status: Literal["ok"]
    service: Literal["leakguard-ai"]
    api_version: Literal["v1"]
    service_version: str
