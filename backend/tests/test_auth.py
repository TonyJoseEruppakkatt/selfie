
def test_user_registration(client):

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "phone_number": "9876543210",
            "password": "Test@12345"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Test User"
    assert data["email"] == "test@example.com"

    # Password must not be returned
    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_email_registration(client):

    user_data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "phone_number": "9876543210",
        "password": "Test@12345"
    }

    client.post(
        "/api/auth/register",
        json=user_data
    )

    response = client.post(
        "/api/auth/register",
        json=user_data
    )

    assert response.status_code == 409


def test_user_login(client):

    client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "phone_number": "9876543210",
            "password": "Test@12345"
        }
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "Test@12345"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_login(client):

    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "Wrong@12345"
        }
    )

    assert response.status_code == 401


def test_access_profile_without_token(client):

    response = client.get(
        "/api/auth/me"
    )

    assert response.status_code == 401


def test_access_profile_with_token(client):

    client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "phone_number": "9876543210",
            "password": "Test@12345"
        }
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "Test@12345"
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_invalid_registration_data(client):

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "A",
            "email": "invalid-email",
            "phone_number": "123",
            "password": "123"
        }
    )

    assert response.status_code == 422
