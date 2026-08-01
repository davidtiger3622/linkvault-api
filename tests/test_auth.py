def test_register_creates_user(client):
    response = client.post("/auth/register", json={"email": "test@example.com", "password": "testpass123"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_register_duplicate_email_fails(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "testpass123"})
    response = client.post("/auth/register", json={"email": "dup@example.com", "password": "testpass123"})
    assert response.status_code == 400


def test_login_with_correct_credentials(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "testpass123"})
    response = client.post("/auth/login", json={"email": "login@example.com", "password": "testpass123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_with_wrong_password_fails(client):
    client.post("/auth/register", json={"email": "wrongpass@example.com", "password": "testpass123"})
    response = client.post("/auth/login", json={"email": "wrongpass@example.com", "password": "wrongpassword"})
    assert response.status_code == 401


def test_refresh_returns_new_tokens(client):
    client.post("/auth/register", json={"email": "refresh@example.com", "password": "testpass123"})
    login_response = client.post("/auth/login", json={"email": "refresh@example.com", "password": "testpass123"})
    refresh_token = login_response.json()["refresh_token"]

    response = client.post(f"/auth/refresh?refresh_token={refresh_token}")
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_with_nonexistent_user_fails(client):
    response = client.post("/auth/login", json={"email": "ghost@example.com", "password": "whatever123"})
    assert response.status_code == 401


def test_refresh_with_invalid_token_fails(client):
    response = client.post("/auth/refresh?refresh_token=not-a-real-token")
    assert response.status_code == 401


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
