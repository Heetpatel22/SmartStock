def test_login_success(client):
    response = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "Password123!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_login_rejects_wrong_password(client):
    response = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "wrong-password"},
        follow_redirects=True,
    )
    assert b"Incorrect email or password" in response.data
