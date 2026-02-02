from __future__ import annotations

import uuid

from models.scenario.scenario import Scenario


class SessionData:
    """Holds a scenario and its cached results."""

    def __init__(
        self,
        scenario: Scenario,
        results: dict[str, list[float]] | None = None,
    ) -> None:
        self.scenario = scenario
        self.results = results


class SessionStore:
    """In-memory session store keyed by UUID."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionData] = {}

    def create(self, scenario: Scenario) -> str:
        session_id = uuid.uuid4().hex
        self._sessions[session_id] = SessionData(scenario=scenario)
        return session_id

    def get(self, session_id: str) -> SessionData | None:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def list_sessions(self) -> list[dict[str, str]]:
        return [
            {"session_id": sid, "name": data.scenario.name}
            for sid, data in self._sessions.items()
        ]


store = SessionStore()
