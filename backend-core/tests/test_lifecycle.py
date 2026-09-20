import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User, UserRole
from src.models.service import Service
from src.models.window import Window
from src.models.ticket import Ticket, TicketStatus
from src.core.security import hash_password, create_access_token

@pytest.mark.asyncio
async def test_ticket_state_machine_and_lifecycle(client: AsyncClient, db_session: AsyncSession):
    operator = User(username="op_flow", hashed_password=hash_password("p"), role=UserRole.OPERATOR)
    service = Service(name="Обмен валюты", prefix="E")
    db_session.add_all([operator, service])
    await db_session.flush()

    window = Window(number=10, name="Окно 10", services=[service])
    db_session.add(window)
    await db_session.commit()

    token = create_access_token({"sub": operator.username, "role": operator.role.value})
    headers = {"Authorization": f"Bearer {token}"}

    t_resp = await client.post("/api/v1/tickets", json={"service_id": service.id, "priority": 0})
    ticket_id = t_resp.json()["id"]

    res_bad_start = await client.post(f"/api/v1/windows/tickets/{ticket_id}/start", headers=headers)
    assert res_bad_start.status_code == 400

    res_bad_comp = await client.post(f"/api/v1/windows/tickets/{ticket_id}/complete", headers=headers)
    assert res_bad_comp.status_code == 400

    call_resp = await client.post(f"/api/v1/windows/{window.id}/call-next", headers=headers)
    assert call_resp.status_code == 200
    assert call_resp.json()["id"] == ticket_id
    assert call_resp.json()["status"] == TicketStatus.CALLED.value

    start_resp = await client.post(f"/api/v1/windows/tickets/{ticket_id}/start", headers=headers)
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == TicketStatus.IN_SERVICE.value

    comp_resp = await client.post(f"/api/v1/windows/tickets/{ticket_id}/complete", headers=headers)
    assert comp_resp.status_code == 200
    assert comp_resp.json()["status"] == TicketStatus.COMPLETED.value

    miss_resp = await client.post(f"/api/v1/windows/tickets/{ticket_id}/missed", headers=headers)
    assert miss_resp.status_code == 400
