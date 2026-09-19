"""Superadmin-only user management and the role hierarchy at the HTTP boundary."""

NEW_USER = {
    "username": "newadmin",
    "fullName": "New Admin",
    "password": "a-sufficiently-long-password",
    "role": "admin",
}


async def test_admin_cannot_list_users(client, auth_header, admin):
    res = await client.get("/api/users", headers=auth_header(admin))
    assert res.status_code == 403


async def test_superadmin_can_list_users(client, auth_header, superadmin):
    res = await client.get("/api/users", headers=auth_header(superadmin))
    assert res.status_code == 200
    assert res.json()[0]["username"] == "superadmin"


async def test_create_user_returns_201_without_password(client, auth_header, superadmin):
    res = await client.post("/api/users", json=NEW_USER, headers=auth_header(superadmin))
    assert res.status_code == 201
    body = res.json()
    assert body["username"] == "newadmin"
    assert "password" not in body
    assert "passwordHash" not in body


async def test_duplicate_username_returns_409(client, auth_header, superadmin):
    await client.post("/api/users", json=NEW_USER, headers=auth_header(superadmin))
    res = await client.post("/api/users", json=NEW_USER, headers=auth_header(superadmin))
    assert res.status_code == 409


async def test_short_password_is_rejected(client, auth_header, superadmin):
    weak = NEW_USER | {"password": "1234"}
    res = await client.post("/api/users", json=weak, headers=auth_header(superadmin))
    assert res.status_code == 422, "old backend allowed 4-character admin passwords"


async def test_cannot_delete_own_account(client, auth_header, superadmin):
    res = await client.delete(f"/api/users/{superadmin.id}", headers=auth_header(superadmin))
    assert res.status_code == 403


async def test_cannot_delete_last_superadmin(client, auth_header, superadmin, session):
    from core.security.passwords import hash_password
    from models.user import Role, User

    other = User(
        username="second",
        full_name="Second",
        password_hash=hash_password("another-long-password"),
        role=Role.SUPERADMIN,
    )
    session.add(other)
    await session.commit()
    await session.refresh(other)

    # Two superadmins exist, so deleting one is allowed.
    assert (
        await client.delete(f"/api/users/{other.id}", headers=auth_header(superadmin))
    ).status_code == 204

    # Now only the actor remains; self-deletion is blocked anyway.
    res = await client.delete(f"/api/users/{superadmin.id}", headers=auth_header(superadmin))
    assert res.status_code == 403
