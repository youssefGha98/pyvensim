from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import ShockRequest, ShockResponse
from api.session import store

router = APIRouter()


@router.post("/{session_id}/shocks", response_model=ShockResponse)
def apply_shock(session_id: str, request: ShockRequest) -> ShockResponse:
    """Apply a shock over a period and return results."""
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    components = {
        name: {
            "component_type": shock.component_type,
            "shock_value": shock.shock_value,
            "start_time": shock.start_time,
            "end_time": shock.end_time,
        }
        for name, shock in request.components.items()
    }

    try:
        session.scenario.apply_shock_over_period(
            components, until=request.simulation_time, dt=request.dt
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    session.results = session.scenario.results
    return ShockResponse(
        session_id=session_id, results=session.scenario.results
    )
