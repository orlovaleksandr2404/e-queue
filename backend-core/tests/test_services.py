import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User, UserRole
from src.models.service import Service
from src.models.ticket import Ticket, TicketStatus
from src.core.security import hash_password, create_access_token

@pytest.mark.asyncio
async def test_service_lifecycle_and_deletion_protection(client: AsyncClient, db_session: AsyncSession):
    admin = User(username="admin_srv", hashed_password=hash_password("p"), role=UserRole.ADMIN)
    operator = User(username="op_srv", hashed_password=hash_password("p"), role=UserRole.OPERATOR)
    db_session.add_all([admin, operator])
    await db_session.commit()

    admin_token = create_access_token({"sub": admin.username, "role": admin.role.value})
    op_token = create_access_token({"sub": operator.username, "role": operator.role.value})

    create_resp = await client.post(
        "/api/v1/services",
        json={"name": "Консультация", "prefix": "K", "avg_duration_minutes": 15},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_resp.status_code == 201
    service_id = create_resp.json()["id"]

    resp_op_del = await client.delete(
        f"/api/v1/services/{service_id}",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert resp_op_del.status_code == 403

    ticket = Ticket(
        number="K-01",
        service_id=service_id,
        status=TicketStatus.WAITING,
        priority=0
    )
    db_session.add(ticket)
    await db_session.commit()

    resp_blocked = await client.delete(
        f"/api/v1/services/{service_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_blocked.status_code == 400
    assert "Невозможно удалить услугу" in resp_blocked.json()["detail"]

    await db_session.delete(ticket)
    await db_session.commit()

    resp_success = await client.delete(
        f"/api/v1/services/{service_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_success.status_code == 204

    resp_get = await client.get(f"/api/v1/services/{service_id}")
    assert resp_get.status_code == 404
