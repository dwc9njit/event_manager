import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user_model import User, UserRole
from app.utils.security import hash_password
from uuid import uuid4

@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient, admin_token: str, db_session: AsyncSession):
    # Create a user to fetch
    user_id = uuid4()
    user = User(
        id=user_id,
        nickname="testuser",
        first_name="Test",
        last_name="User",
        email="testuser@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.AUTHENTICATED
    )
    db_session.add(user)
    await db_session.commit()

    response = await async_client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"

@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient, admin_token: str):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
        "nickname": "testuser"
    }
    response = await async_client.post("/users/", json=user_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_update_user(async_client: AsyncClient, admin_token: str, db_session: AsyncSession):
    # Create a user to update
    user_id = uuid4()
    user = User(
        id=user_id,
        nickname="testuser",
        first_name="Test",
        last_name="User",
        email="testuser@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.AUTHENTICATED
    )
    db_session.add(user)
    await db_session.commit()

    user_update_data = {
        "first_name": "Updated",
        "last_name": "User",
        "nickname": "updateduser"
    }
    response = await async_client.put(f"/users/{user_id}", json=user_update_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"

@pytest.mark.asyncio
async def test_delete_user(async_client: AsyncClient, admin_token: str, db_session: AsyncSession):
    # Create a user to delete
    user_id = uuid4()
    user = User(
        id=user_id,
        nickname="testuser",
        first_name="Test",
        last_name="User",
        email="testuser@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.AUTHENTICATED
    )
    db_session.add(user)
    await db_session.commit()

    response = await async_client.delete(f"/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_list_users(async_client: AsyncClient, admin_token: str):
    response = await async_client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

@pytest.mark.asyncio
async def test_get_user_not_found(async_client: AsyncClient, admin_token: str):
    response = await async_client.get("/users/00000000-0000-0000-0000-000000000000", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_user_existing_email(async_client: AsyncClient, admin_token: str, db_session: AsyncSession):
    existing_user = User(
        id=uuid4(),
        nickname="testuser",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.AUTHENTICATED
    )
    db_session.add(existing_user)
    await db_session.commit()

    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
        "nickname": "testuser2"
    }
    response = await async_client.post("/users/", json=user_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_update_user_not_found(async_client: AsyncClient, admin_token: str):
    user_update_data = {
        "first_name": "Updated",
        "last_name": "User",
        "nickname": "updateduser"
    }
    response = await async_client.put("/users/00000000-0000-0000-0000-000000000000", json=user_update_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_user_not_found(async_client: AsyncClient, admin_token: str):
    response = await async_client.delete("/users/00000000-0000-0000-0000-000000000000", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_users_with_pagination(async_client: AsyncClient, admin_token: str, db_session: AsyncSession):
    # Fetch the count of existing users
    result = await db_session.execute(select(User))
    existing_users = result.scalars().all()
    existing_user_count = len(existing_users)
    
    # Create multiple users to test pagination
    for _ in range(15):
        user = User(
            id=uuid4(),
            nickname=f"testuser{_}",
            first_name="Test",
            last_name="User",
            email=f"testuser{_}@example.com",
            hashed_password=hash_password("password123"),
            role=UserRole.AUTHENTICATED
        )
        db_session.add(user)
    await db_session.commit()

    response = await async_client.get("/users/?skip=0&limit=10", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == existing_user_count + 15
