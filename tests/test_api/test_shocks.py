from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient


class TestShocks:
    def test_apply_auxiliary_shock(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        create_resp = client.post("/scenarios/", json=sir_payload)
        sid = create_resp.json()["session_id"]

        resp = client.post(
            f"/scenarios/{sid}/shocks",
            json={
                "components": {
                    "transmission_rate": {
                        "component_type": "auxiliary",
                        "shock_value": 0.1,
                        "start_time": 5,
                        "end_time": 10,
                    }
                },
                "simulation_time": 20,
                "dt": 1,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["results"] is not None

    def test_invalid_time_range(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        create_resp = client.post("/scenarios/", json=sir_payload)
        sid = create_resp.json()["session_id"]

        resp = client.post(
            f"/scenarios/{sid}/shocks",
            json={
                "components": {
                    "transmission_rate": {
                        "component_type": "auxiliary",
                        "shock_value": 0.1,
                        "start_time": 10,
                        "end_time": 5,
                    }
                },
                "simulation_time": 20,
                "dt": 1,
            },
        )
        assert resp.status_code == 422

    def test_shock_unknown_session(self, client: TestClient) -> None:
        resp = client.post(
            "/scenarios/unknown123/shocks",
            json={
                "components": {
                    "x": {
                        "component_type": "auxiliary",
                        "shock_value": 1,
                        "start_time": 0,
                        "end_time": 5,
                    }
                }
            },
        )
        assert resp.status_code == 404
