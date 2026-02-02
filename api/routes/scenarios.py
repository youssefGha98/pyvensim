from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from api.expression import ExpressionError, compile_rate_function
from api.schemas import (
    CreateScenarioRequest,
    CreateScenarioResponse,
    ResultsResponse,
    RunRequest,
    RunResponse,
    SessionListResponse,
)
from api.session import store
from models.core.auxiliary import Auxiliary
from models.scenario.scenario import Scenario

router = APIRouter()


@router.get("/", response_model=SessionListResponse)
def list_scenarios() -> SessionListResponse:
    """List all active sessions."""
    return SessionListResponse(sessions=store.list_sessions())


@router.post("/", response_model=CreateScenarioResponse, status_code=201)
def create_scenario(request: CreateScenarioRequest) -> CreateScenarioResponse:
    """Create a scenario from a full model definition."""
    auxiliaries: list[Auxiliary] = []
    for aux_schema in request.auxiliaries:
        auxiliaries.append(Auxiliary(aux_schema.name, aux_schema.values))

    rates: dict[str, dict[str, Any]] = {}
    for rate_name, rate_schema in request.rates.items():
        try:
            rate_fn = compile_rate_function(
                rate_schema.expression, rate_schema.params
            )
        except ExpressionError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid expression for rate '{rate_name}': {e}",
            ) from e

        rates[rate_name] = {
            "rate_function": rate_fn,
            "source": rate_schema.source,
            "destination": rate_schema.destination,
        }

    scenario = Scenario(
        name=request.name,
        initial_values=dict(request.initial_values),
        rates=rates,
        auxiliaries=auxiliaries,
    )

    session_id = store.create(scenario)

    return CreateScenarioResponse(
        session_id=session_id,
        name=request.name,
        message="Scenario created successfully",
    )


@router.post("/{session_id}/run", response_model=RunResponse)
def run_scenario(session_id: str, request: RunRequest) -> RunResponse:
    """Run the simulation for the given scenario."""
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Reset auxiliary timesteps before each run
    for aux in session.scenario.auxiliaries:
        aux.current_time_step = 0

    try:
        results = session.scenario.run(request.simulation_time, request.dt)
    except (ValueError, ZeroDivisionError, OverflowError) as e:
        raise HTTPException(
            status_code=422, detail=f"Simulation error: {e}"
        ) from e

    session.results = results
    return RunResponse(session_id=session_id, results=results)


@router.get("/{session_id}/results", response_model=ResultsResponse)
def get_results(session_id: str) -> ResultsResponse:
    """Retrieve cached results from the last run."""
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return ResultsResponse(
        session_id=session_id,
        has_results=session.results is not None,
        results=session.results,
    )


@router.delete("/{session_id}", status_code=204)
def delete_scenario(session_id: str) -> None:
    """Delete a session."""
    if not store.delete(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
