import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User, UserRole
from src.models.service import Service
from src.core.security import hash_password, create_access_token

@pytest.mark.asyncio
async def test_windows_management_and_rbac(client: AsyncClient, db_session: AsyncSession):
    admin = User(username="admin_win", hashed_password=hash_password("p"), role=UserRole.ADMIN)
    operator = User(username="op_win", hashed_password=hash_password("p"), role=UserRole.OPERATOR)
    service = Service(name="Быстрые платежи", prefix="P")
    db_session.add_all([admin, operator, service])
    await db_session.commit()

    admin_token = create_access_token({"sub": admin.username, "role": admin.role.value})
    op_token = create_access_token({"sub": operator.username, "role": operator.role.value})

    resp_forbidden = await client.post(
        "/api/v1/windows",
        json={"number": 1, "name": "Окно 1", "service_ids": [service.id]},
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert resp_forbidden.status_code == 403

    resp_create = await client.post(
        "/api/v1/windows",
        json={"number": 1, "name": "Окно 1", "service_ids": [service.id]},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_create.status_code == 201
    win_data = resp_create.json()
    assert win_data["number"] == 1
    assert win_data["name"] == "Окно 1"
    assert len(win_data["services"]) == 1
    assert win_data["services"][0]["id"] == service.id

    resp_dup = await client.post(
        "/api/v1/windows",
        json={"number": 1, "name": "Другое окно 1", "service_ids": []},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_dup.status_code == 400

    resp_list = await client.get("/api/v1/windows")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) == 1
