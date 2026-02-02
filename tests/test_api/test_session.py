from __future__ import annotations

from models.core.auxiliary import Auxiliary
from models.scenario.scenario import Scenario

from api.session import SessionStore


def _make_scenario(name: str = "test") -> Scenario:
    return Scenario(
        name=name,
        initial_values={"x": 0},
        rates={},
        auxiliaries=[Auxiliary("a", 1.0)],
    )


class TestSessionStore:
    def test_create_returns_unique_ids(self) -> None:
        store = SessionStore()
        id1 = store.create(_make_scenario("s1"))
        id2 = store.create(_make_scenario("s2"))
        assert id1 != id2

    def test_get_existing(self) -> None:
        store = SessionStore()
        sid = store.create(_make_scenario())
        session = store.get(sid)
        assert session is not None
        assert session.scenario.name == "test"

    def test_get_unknown_returns_none(self) -> None:
        store = SessionStore()
        assert store.get("nonexistent") is None

    def test_delete_existing(self) -> None:
        store = SessionStore()
        sid = store.create(_make_scenario())
        assert store.delete(sid) is True
        assert store.get(sid) is None

    def test_delete_unknown_returns_false(self) -> None:
        store = SessionStore()
        assert store.delete("nonexistent") is False

    def test_list_sessions(self) -> None:
        store = SessionStore()
        store.create(_make_scenario("alpha"))
        store.create(_make_scenario("beta"))
        sessions = store.list_sessions()
        assert len(sessions) == 2
        names = {s["name"] for s in sessions}
        assert names == {"alpha", "beta"}
