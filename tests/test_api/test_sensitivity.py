from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient


class TestSensitivityUnivariate:
    def test_univariate_returns_results(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        create_resp = client.post("/scenarios/", json=sir_payload)
        sid = create_resp.json()["session_id"]

        resp = client.post(
            f"/scenarios/{sid}/sensitivity/univariate",
            json={
                "component_name": "stocks",
                "parameter": "susceptible",
                "range_values": [40, 60],
                "simulation_time": 10,
                "dt": 1,
            },
        )
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 2

    def test_univariate_unknown_session(self, client: TestClient) -> None:
        resp = client.post(
            "/scenarios/unknown123/sensitivity/univariate",
            json={
                "component_name": "stocks",
                "parameter": "x",
                "range_values": [1, 2],
            },
        )
        assert resp.status_code == 404


class TestSensitivityMultivariate:
    def test_multivariate_returns_results(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        create_resp = client.post("/scenarios/", json=sir_payload)
        sid = create_resp.json()["session_id"]

        resp = client.post(
            f"/scenarios/{sid}/sensitivity/multivariate",
            json={
                "parameters": [
                    {"component": "stocks", "name": "susceptible"},
                    {"component": "stocks", "name": "infected"},
                ],
                "combinations": [[40, 5], [60, 15]],
                "simulation_time": 10,
                "dt": 1,
            },
        )
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 2

    def test_multivariate_unknown_session(self, client: TestClient) -> None:
        resp = client.post(
            "/scenarios/unknown123/sensitivity/multivariate",
            json={
                "parameters": [{"component": "stocks", "name": "x"}],
                "combinations": [[1]],
            },
        )
        assert resp.status_code == 404
