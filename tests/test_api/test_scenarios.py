from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


class TestCreateScenario:
    def test_create_returns_201(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        resp = client.post("/scenarios/", json=sir_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert "session_id" in data
        assert data["name"] == "SIR Model"

    def test_create_invalid_expression(self, client: TestClient) -> None:
        payload = {
            "name": "Bad",
            "initial_values": {"x": 0},
            "rates": {
                "flow": {
                    "expression": "__import__('os')",
                    "params": [],
                    "source": None,
                    "destination": "x",
                }
            },
            "auxiliaries": [],
        }
        resp = client.post("/scenarios/", json=payload)
        assert resp.status_code == 422

    def test_create_missing_fields(self, client: TestClient) -> None:
        resp = client.post("/scenarios/", json={"name": "Incomplete"})
        assert resp.status_code == 422


class TestListScenarios:
    def test_list_empty(self, client: TestClient) -> None:
        resp = client.get("/scenarios/")
        assert resp.status_code == 200
        assert resp.json()["sessions"] == []

    def test_list_after_create(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        client.post("/scenarios/", json=sir_payload)
        resp = client.get("/scenarios/")
        assert len(resp.json()["sessions"]) == 1


class TestDeleteScenario:
    def test_delete_existing(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        create_resp = client.post("/scenarios/", json=sir_payload)
        sid = create_resp.json()["session_id"]
        resp = client.delete(f"/scenarios/{sid}")
        assert resp.status_code == 204

    def test_delete_unknown(self, client: TestClient) -> None:
        resp = client.delete("/scenarios/unknown123")
        assert resp.status_code == 404


class TestRunScenario:
    def test_run_returns_results(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        create_resp = client.post("/scenarios/", json=sir_payload)
        sid = create_resp.json()["session_id"]

        run_resp = client.post(
            f"/scenarios/{sid}/run",
            json={"simulation_time": 10, "dt": 1},
        )
        assert run_resp.status_code == 200
        results = run_resp.json()["results"]
        assert "time" in results
        assert "susceptible" in results
        assert "infected" in results
        assert "recovered" in results

    def test_sir_conservation(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        create_resp = client.post("/scenarios/", json=sir_payload)
        sid = create_resp.json()["session_id"]

        run_resp = client.post(
            f"/scenarios/{sid}/run",
            json={"simulation_time": 100, "dt": 1},
        )
        results = run_resp.json()["results"]
        total_initial = 50 + 10 + 0
        for i in range(len(results["time"])):
            total = (
                results["susceptible"][i]
                + results["infected"][i]
                + results["recovered"][i]
            )
            assert total == pytest.approx(total_initial, abs=1e-6)

    def test_run_unknown_session(self, client: TestClient) -> None:
        resp = client.post(
            "/scenarios/unknown123/run",
            json={"simulation_time": 10, "dt": 1},
        )
        assert resp.status_code == 404

    def test_run_invalid_params(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        create_resp = client.post("/scenarios/", json=sir_payload)
        sid = create_resp.json()["session_id"]

        resp = client.post(
            f"/scenarios/{sid}/run",
            json={"simulation_time": -1, "dt": 1},
        )
        assert resp.status_code == 422


class TestGetResults:
    def test_no_results_before_run(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        create_resp = client.post("/scenarios/", json=sir_payload)
        sid = create_resp.json()["session_id"]

        resp = client.get(f"/scenarios/{sid}/results")
        assert resp.status_code == 200
        assert resp.json()["has_results"] is False

    def test_results_after_run(
        self, client: TestClient, sir_payload: dict[str, Any]
    ) -> None:
        create_resp = client.post("/scenarios/", json=sir_payload)
        sid = create_resp.json()["session_id"]

        client.post(
            f"/scenarios/{sid}/run",
            json={"simulation_time": 10, "dt": 1},
        )

        resp = client.get(f"/scenarios/{sid}/results")
        assert resp.status_code == 200
        assert resp.json()["has_results"] is True
        assert "time" in resp.json()["results"]

    def test_results_unknown_session(self, client: TestClient) -> None:
        resp = client.get("/scenarios/unknown123/results")
        assert resp.status_code == 404
