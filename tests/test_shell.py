from __future__ import annotations


def test_healthz(client):
    response = client.get("/healthz/")
    assert response.status_code == 200
    assert response.content == b"ok"


def test_dashboard_shell(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Prevádzkový prehľad" in response.content.decode("utf-8")
