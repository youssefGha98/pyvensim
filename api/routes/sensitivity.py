from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import (
    SensitivityMultivariateRequest,
    SensitivityResponse,
    SensitivityUnivariateRequest,
)
from api.session import store

router = APIRouter()


@router.post(
    "/{session_id}/sensitivity/univariate",
    response_model=SensitivityResponse,
)
def run_sensitivity_univariate(
    session_id: str, request: SensitivityUnivariateRequest
) -> SensitivityResponse:
    """Run univariate sensitivity analysis."""
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    raw_results = session.scenario.run_sensitivity_analysis_univariate(
        component_name=request.component_name,
        parameter=request.parameter,
        range_values=request.range_values,
        until=request.simulation_time,
        dt=request.dt,
    )

    results = {str(k): v for k, v in raw_results.items()}
    return SensitivityResponse(session_id=session_id, results=results)


@router.post(
    "/{session_id}/sensitivity/multivariate",
    response_model=SensitivityResponse,
)
def run_sensitivity_multivariate(
    session_id: str, request: SensitivityMultivariateRequest
) -> SensitivityResponse:
    """Run multivariate sensitivity analysis."""
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    combinations = [tuple(c) for c in request.combinations]

    raw_results = session.scenario.run_sensitivity_analysis_multivariate(
        parameters=request.parameters,
        param_combinations=combinations,
        until=request.simulation_time,
        dt=request.dt,
    )

    results = {str(k): v for k, v in raw_results.items()}
    return SensitivityResponse(session_id=session_id, results=results)
