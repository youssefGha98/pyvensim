from __future__ import annotations

from pydantic import BaseModel, Field


class AuxiliarySchema(BaseModel):
    """An auxiliary variable: constant, time-series list, or null."""

    name: str
    values: float | list[float] | None = None


class RateSchema(BaseModel):
    """A flow's rate definition with a math expression string."""

    expression: str
    params: list[str]
    source: str | None = None
    destination: str | None = None
    add_noise: bool = False
    sensitivity: float = 0.1


class CreateScenarioRequest(BaseModel):
    """Full model definition sent by the frontend."""

    name: str
    initial_values: dict[str, float]
    rates: dict[str, RateSchema]
    auxiliaries: list[AuxiliarySchema]


class RunRequest(BaseModel):
    """Parameters for running a simulation."""

    simulation_time: float = Field(gt=0)
    dt: float = Field(gt=0, default=1.0)


class SensitivityUnivariateRequest(BaseModel):
    """Request for univariate sensitivity analysis."""

    component_name: str
    parameter: str
    range_values: list[float]
    simulation_time: float = Field(gt=0, default=100)
    dt: float = Field(gt=0, default=1.0)


class SensitivityMultivariateRequest(BaseModel):
    """Request for multivariate sensitivity analysis."""

    parameters: list[dict[str, str]]
    combinations: list[list[float]]
    simulation_time: float = Field(gt=0, default=100)
    dt: float = Field(gt=0, default=1.0)


class ShockComponentSchema(BaseModel):
    """A single shock component definition."""

    component_type: str
    shock_value: float
    start_time: int
    end_time: int


class ShockRequest(BaseModel):
    """Request to apply shocks over a period."""

    components: dict[str, ShockComponentSchema]
    simulation_time: float = Field(gt=0, default=100)
    dt: float = Field(gt=0, default=1.0)


# ── Response Models ──


class CreateScenarioResponse(BaseModel):
    session_id: str
    name: str
    message: str


class RunResponse(BaseModel):
    session_id: str
    results: dict[str, list[float]]


class ResultsResponse(BaseModel):
    session_id: str
    has_results: bool
    results: dict[str, list[float]] | None = None


class SensitivityResponse(BaseModel):
    session_id: str
    results: dict[str, dict[str, list[float]]]


class ShockResponse(BaseModel):
    session_id: str
    results: dict[str, list[float]] | None = None


class SessionListResponse(BaseModel):
    sessions: list[dict[str, str]]


class ErrorResponse(BaseModel):
    detail: str
