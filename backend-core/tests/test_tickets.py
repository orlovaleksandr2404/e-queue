import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.service import Service
from src.models.ticket import TicketStatus

@pytest.mark.asyncio
async def test_issue_ticket_lifecycle(client: AsyncClient, db_session: AsyncSession):
    service_a = Service(
        name="Оформление карт",
        prefix="A"
    )
    service_b = Service(
        name="Кредиты",
        prefix="B"
    )
    db_session.add_all([service_a, service_b])
    await db_session.commit()

    resp1 = await client.post("/api/v1/tickets", json={"service_id": service_a.id, "priority": 0})
    assert resp1.status_code == 201
    data1 = resp1.json()
    assert data1["number"] == "A-01"
    assert data1["status"] == TicketStatus.WAITING.value
    assert data1["priority"] == 0

    resp2 = await client.post("/api/v1/tickets", json={"service_id": service_a.id, "priority": 5})
    assert resp2.status_code == 201
    data2 = resp2.json()
    assert data2["number"] == "A-02"
    assert data2["priority"] == 5

    resp3 = await client.post("/api/v1/tickets", json={"service_id": service_b.id, "priority": 0})
    assert resp3.status_code == 201
    assert resp3.json()["number"] == "B-01"

    resp_err = await client.post("/api/v1/tickets", json={"service_id": 9999, "priority": 0})
    assert resp_err.status_code == 404
