"""Auth behaviour, including the removal of the publicly-open register endpoint."""

PASSWORD = "correct-horse-battery"


async def test_login_returns_token(client, admin):
    res = await client.post("/api/auth/login", json={"username": "admin", "password": PASSWORD})
    assert res.status_code == 200
    body = res.json()
    assert body["accessToken"]
    assert body["tokenType"] == "bearer"
    assert body["expiresIn"] == 180 * 60


async def test_login_rejects_wrong_password(client, admin):
    res = await client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert res.status_code == 401


async def test_login_does_not_reveal_whether_user_exists(client, admin):
    missing = await client.post(
        "/api/auth/login", json={"username": "nobody", "password": PASSWORD}
    )
    wrong = await client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert missing.status_code == wrong.status_code == 401
    assert missing.json()["detail"] == wrong.json()["detail"]


async def test_public_register_endpoint_no_longer_exists(client):
    res = await client.post(
        "/api/auth/register", json={"username": "attacker", "password": "hunter2xxxxx"}
    )
    assert res.status_code == 404


async def test_me_returns_current_user(client, auth_header, admin):
    res = await client.get("/api/auth/me", headers=auth_header(admin))
    assert res.status_code == 200
    body = res.json()
    assert body["username"] == "admin"
    assert body["role"] == "admin"
    assert body["fullName"] == "Admin"
    assert "passwordHash" not in body


async def test_me_rejects_garbage_token(client):
    res = await client.get("/api/auth/me", headers={"Authorization": "Bearer nonsense"})
    assert res.status_code == 401
