import pytest
from fastapi.testclient import TestClient

from src.core.config import settings
from src.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _set_event_key(monkeypatch):
    monkeypatch.setattr(settings, "EVENT_API_KEY", "test-secret-key")
    yield


def test_broadcast_missing_key_401(client):
    r = client.post("/api/v1/events/broadcast", json={"type": "queue_update", "payload": {}})
    assert r.status_code == 401


def test_broadcast_wrong_key_401(client):
    r = client.post(
        "/api/v1/events/broadcast",
        json={"type": "queue_update", "payload": {}},
        headers={"X-Api-Key": "wrong"},
    )
    assert r.status_code == 401


def test_broadcast_correct_key_no_clients(client):
    r = client.post(
        "/api/v1/events/broadcast",
        json={"type": "queue_update", "payload": {}},
        headers={"X-Api-Key": "test-secret-key"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body == {"ok": True, "delivered": 0}


def test_broadcast_delivers_to_websocket(client):
    with client.websocket_connect("/ws/queue") as ws:
        r = client.post(
            "/api/v1/events/broadcast",
            json={"type": "ticket_called", "payload": {"number": "A-005", "window": 2}},
            headers={"X-Api-Key": "test-secret-key"},
        )
        assert r.status_code == 200
        assert r.json()["delivered"] == 1

        msg = ws.receive_json()
        assert msg["type"] == "ticket_called"
        assert msg["payload"]["number"] == "A-005"
        assert msg["payload"]["window"] == 2


def test_broadcast_two_clients(client):
    with client.websocket_connect("/ws/queue") as ws1, \
         client.websocket_connect("/ws/queue") as ws2:
        r = client.post(
            "/api/v1/events/broadcast",
            json={"type": "queue_update", "payload": {"x": 1}},
            headers={"X-Api-Key": "test-secret-key"},
        )
        assert r.json()["delivered"] == 2
        assert ws1.receive_json()["type"] == "queue_update"
        assert ws2.receive_json()["type"] == "queue_update"


def test_broadcast_empty_type_rejected(client):
    r = client.post(
        "/api/v1/events/broadcast",
        json={"type": "", "payload": {}},
        headers={"X-Api-Key": "test-secret-key"},
    )
    assert r.status_code == 422


def test_broadcast_open_when_no_key_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "EVENT_API_KEY", "")
    r = client.post(
        "/api/v1/events/broadcast",
        json={"type": "queue_update", "payload": {}},
    )
    assert r.status_code == 200