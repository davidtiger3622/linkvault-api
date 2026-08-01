import pytest


@pytest.fixture()
def auth_headers(client):
    client.post("/auth/register", json={"email": "bookmarks@example.com", "password": "testpass123"})
    login_response = client.post("/auth/login", json={"email": "bookmarks@example.com", "password": "testpass123"})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def other_user_headers(client):
    client.post("/auth/register", json={"email": "other@example.com", "password": "testpass123"})
    login_response = client.post("/auth/login", json={"email": "other@example.com", "password": "testpass123"})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_bookmark(client, auth_headers):
    response = client.post("/bookmarks", json={"name": "GitHub", "url": "https://github.com"}, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "GitHub"
    assert data["favicon_url"] is not None
    assert data["is_favorite"] is False


def test_create_bookmark_without_auth_fails(client):
    response = client.post("/bookmarks", json={"name": "GitHub", "url": "https://github.com"})
    assert response.status_code == 401


def test_create_duplicate_url_fails(client, auth_headers):
    client.post("/bookmarks", json={"name": "GitHub", "url": "https://github.com"}, headers=auth_headers)
    response = client.post("/bookmarks", json={"name": "GitHub Again", "url": "https://github.com"}, headers=auth_headers)
    assert response.status_code == 409


def test_list_bookmarks_returns_only_own(client, auth_headers, other_user_headers):
    client.post("/bookmarks", json={"name": "Mine", "url": "https://mine.com"}, headers=auth_headers)
    client.post("/bookmarks", json={"name": "Theirs", "url": "https://theirs.com"}, headers=other_user_headers)

    response = client.get("/bookmarks", headers=auth_headers)
    assert response.status_code == 200
    names = [b["name"] for b in response.json()]
    assert "Mine" in names
    assert "Theirs" not in names


def test_search_filters_by_name(client, auth_headers):
    client.post("/bookmarks", json={"name": "GitHub", "url": "https://github.com"}, headers=auth_headers)
    client.post("/bookmarks", json={"name": "Reddit", "url": "https://reddit.com"}, headers=auth_headers)

    response = client.get("/bookmarks?search=git", headers=auth_headers)
    names = [b["name"] for b in response.json()]
    assert "GitHub" in names
    assert "Reddit" not in names


def test_search_filters_by_url(client, auth_headers):
    client.post("/bookmarks", json={"name": "GitHub", "url": "https://github.com"}, headers=auth_headers)
    response = client.get("/bookmarks?search=github.com", headers=auth_headers)
    assert len(response.json()) == 1


def test_sort_alphabetical(client, auth_headers):
    client.post("/bookmarks", json={"name": "Zebra", "url": "https://zebra.com"}, headers=auth_headers)
    client.post("/bookmarks", json={"name": "Apple", "url": "https://apple.com"}, headers=auth_headers)

    response = client.get("/bookmarks?sort=alphabetical", headers=auth_headers)
    names = [b["name"] for b in response.json()]
    assert names == sorted(names)


def test_update_bookmark_name(client, auth_headers):
    create_response = client.post("/bookmarks", json={"name": "Old Name", "url": "https://example.com"}, headers=auth_headers)
    bookmark_id = create_response.json()["id"]

    response = client.patch(f"/bookmarks/{bookmark_id}", json={"name": "New Name"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_toggle_favorite(client, auth_headers):
    create_response = client.post("/bookmarks", json={"name": "Favme", "url": "https://favme.com"}, headers=auth_headers)
    bookmark_id = create_response.json()["id"]

    response = client.patch(f"/bookmarks/{bookmark_id}", json={"is_favorite": True}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_favorite"] is True


def test_update_nonexistent_bookmark_fails(client, auth_headers):
    response = client.patch("/bookmarks/9999", json={"name": "Ghost"}, headers=auth_headers)
    assert response.status_code == 404


def test_cannot_update_another_users_bookmark(client, auth_headers, other_user_headers):
    create_response = client.post("/bookmarks", json={"name": "Mine", "url": "https://mine.com"}, headers=auth_headers)
    bookmark_id = create_response.json()["id"]

    response = client.patch(f"/bookmarks/{bookmark_id}", json={"name": "Hijacked"}, headers=other_user_headers)
    assert response.status_code == 404


def test_delete_bookmark(client, auth_headers):
    create_response = client.post("/bookmarks", json={"name": "Temp", "url": "https://temp.com"}, headers=auth_headers)
    bookmark_id = create_response.json()["id"]

    delete_response = client.delete(f"/bookmarks/{bookmark_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    list_response = client.get("/bookmarks", headers=auth_headers)
    assert bookmark_id not in [b["id"] for b in list_response.json()]


def test_delete_nonexistent_bookmark_fails(client, auth_headers):
    response = client.delete("/bookmarks/9999", headers=auth_headers)
    assert response.status_code == 404

def test_invalid_token_rejected(client):
    response = client.get("/bookmarks", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
