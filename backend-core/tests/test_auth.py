import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User, UserRole
from src.core.security import hash_password, create_access_token

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    user = User(
        username="testadmin",
        hashed_password=hash_password("correctpass"),
        full_name="Test Admin",
        role=UserRole.ADMIN
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testadmin", "password": "correctpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, db_session: AsyncSession):
    user = User(
        username="operator",
        hashed_password=hash_password("correctpass"),
        full_name="Test Operator",
        role=UserRole.OPERATOR
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "operator", "password": "wrongpass"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_require_admin_guard(client: AsyncClient, db_session: AsyncSession):
    operator = User(
        username="regular_op",
        hashed_password=hash_password("pass"),
        role=UserRole.OPERATOR
    )
    db_session.add(operator)

    admin = User(
        username="root_admin",
        hashed_password=hash_password("pass"),
        role=UserRole.ADMIN
    )
    db_session.add(admin)
    await db_session.commit()

    op_token = create_access_token(data={"sub": operator.username, "role": operator.role.value})
    op_response = await client.get(
        "/api/v1/users/operators",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert op_response.status_code == 403

    admin_token = create_access_token(data={"sub": admin.username, "role": admin.role.value})
    admin_response = await client.get(
        "/api/v1/users/operators",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_response.status_code == 200
