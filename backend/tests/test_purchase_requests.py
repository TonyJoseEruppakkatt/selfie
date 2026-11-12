import pytest

from sqlalchemy.orm import Session

from app.models.mobile import Mobile
from app.models.user import User
from app.models.purchase_request import PurchaseRequest
from app.database.session import get_db


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def register_and_login(client, name, email, phone):
    """Register a user and return their login token."""

    registration_data = {
        "full_name": name,
        "email": email,
        "phone_number": phone,
        "password": "TestPassword123"
    }

    register_response = client.post(
        "/api/auth/register",
        json=registration_data
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": "TestPassword123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return token


def create_mobile_listing(seller_id):
    """Create a mobile listing directly in the test database."""

    from conftest import TestingSessionLocal

    db: Session = TestingSessionLocal()

    try:
        mobile = Mobile(
            seller_id=seller_id,
            brand="Samsung",
            model="Galaxy S24",
            price=25000,
            condition="Excellent",
            description="Test mobile listing",
            status="available"
        )

        db.add(mobile)
        db.commit()
        db.refresh(mobile)

        return mobile.id

    finally:
        db.close()


# --------------------------------------------------
# Fixtures
# --------------------------------------------------

@pytest.fixture
def purchase_test_data(client):

    # Register seller
    seller_token = register_and_login(
        client,
        "Test Seller",
        "seller@test.com",
        "9876543210"
    )

    # Register buyer
    buyer_token = register_and_login(
        client,
        "Test Buyer",
        "buyer@test.com",
        "9876543211"
    )

    # Register another user
    other_token = register_and_login(
        client,
        "Other User",
        "other@test.com",
        "9876543212"
    )

    from conftest import TestingSessionLocal

    db = TestingSessionLocal()

    try:
        seller = db.query(User).filter(
            User.email == "seller@test.com"
        ).first()

        buyer = db.query(User).filter(
            User.email == "buyer@test.com"
        ).first()

        other_user = db.query(User).filter(
            User.email == "other@test.com"
        ).first()

        seller_id = seller.id
        buyer_id = buyer.id
        other_user_id = other_user.id

    finally:
        db.close()

    mobile_id = create_mobile_listing(seller_id)

    return {
        "seller_token": seller_token,
        "buyer_token": buyer_token,
        "other_token": other_token,
        "seller_id": seller_id,
        "buyer_id": buyer_id,
        "other_user_id": other_user_id,
        "mobile_id": mobile_id
    }


# --------------------------------------------------
# Test 1: Buyer can send a purchase request
# --------------------------------------------------

def test_create_purchase_request(client, purchase_test_data):

    data = purchase_test_data

    response = client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={
            "message": "I am interested in buying this mobile."
        },
        headers={
            "Authorization": f"Bearer {data['buyer_token']}"
        }
    )

    assert response.status_code == 201

    result = response.json()

    assert result["mobile_id"] == data["mobile_id"]
    assert result["buyer_id"] == data["buyer_id"]
    assert result["seller_id"] == data["seller_id"]
    assert result["status"] == "pending"


# --------------------------------------------------
# Test 2: Cannot request a nonexistent mobile
# --------------------------------------------------

def test_request_nonexistent_mobile(client, purchase_test_data):

    data = purchase_test_data

    response = client.post(
        "/api/purchase-requests/99999",
        json={"message": "Interested"},
        headers={
            "Authorization": f"Bearer {data['buyer_token']}"
        }
    )

    assert response.status_code == 404


# --------------------------------------------------
# Test 3: Seller cannot request own listing
# --------------------------------------------------

def test_seller_cannot_request_own_mobile(client, purchase_test_data):

    data = purchase_test_data

    response = client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={"message": "I want my own mobile"},
        headers={
            "Authorization": f"Bearer {data['seller_token']}"
        }
    )

    assert response.status_code == 400


# --------------------------------------------------
# Test 4: Prevent duplicate active requests
# --------------------------------------------------

def test_prevent_duplicate_purchase_request(client, purchase_test_data):

    data = purchase_test_data

    headers = {
        "Authorization": f"Bearer {data['buyer_token']}"
    }

    first_response = client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={"message": "First request"},
        headers=headers
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={"message": "Second request"},
        headers=headers
    )

    assert second_response.status_code == 409


# --------------------------------------------------
# Test 5: Buyer can view their requests
# --------------------------------------------------

def test_get_buyer_requests(client, purchase_test_data):

    data = purchase_test_data

    client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={"message": "Interested"},
        headers={
            "Authorization": f"Bearer {data['buyer_token']}"
        }
    )

    response = client.get(
        "/api/purchase-requests/buyer",
        headers={
            "Authorization": f"Bearer {data['buyer_token']}"
        }
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# --------------------------------------------------
# Test 6: Seller can view received requests
# --------------------------------------------------

def test_get_seller_requests(client, purchase_test_data):

    data = purchase_test_data

    client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={"message": "Interested"},
        headers={
            "Authorization": f"Bearer {data['buyer_token']}"
        }
    )

    response = client.get(
        "/api/purchase-requests/seller",
        headers={
            "Authorization": f"Bearer {data['seller_token']}"
        }
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# --------------------------------------------------
# Test 7: Other users cannot view the request
# --------------------------------------------------

def test_other_user_cannot_view_request(client, purchase_test_data):

    data = purchase_test_data

    create_response = client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={"message": "Interested"},
        headers={
            "Authorization": f"Bearer {data['buyer_token']}"
        }
    )

    request_id = create_response.json()["id"]

    response = client.get(
        f"/api/purchase-requests/{request_id}",
        headers={
            "Authorization": f"Bearer {data['other_token']}"
        }
    )

    assert response.status_code == 403


# --------------------------------------------------
# Test 8: Seller can accept a purchase request
# --------------------------------------------------

def test_seller_can_accept_request(client, purchase_test_data):

    data = purchase_test_data

    create_response = client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={"message": "Interested"},
        headers={
            "Authorization": f"Bearer {data['buyer_token']}"
        }
    )

    request_id = create_response.json()["id"]

    response = client.patch(
        f"/api/purchase-requests/{request_id}/status",
        json={"status": "accepted"},
        headers={
            "Authorization": f"Bearer {data['seller_token']}"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


# --------------------------------------------------
# Test 9: Buyer cannot accept or reject a request
# --------------------------------------------------

def test_buyer_cannot_update_request_status(client, purchase_test_data):

    data = purchase_test_data

    create_response = client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={"message": "Interested"},
        headers={
            "Authorization": f"Bearer {data['buyer_token']}"
        }
    )

    request_id = create_response.json()["id"]

    response = client.patch(
        f"/api/purchase-requests/{request_id}/status",
        json={"status": "accepted"},
        headers={
            "Authorization": f"Bearer {data['buyer_token']}"
        }
    )

    assert response.status_code == 403


# --------------------------------------------------
# Test 10: Seller can reject a request
# --------------------------------------------------

def test_seller_can_reject_request(client, purchase_test_data):

    data = purchase_test_data

    create_response = client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={"message": "Interested"},
        headers={
            "Authorization": f"Bearer {data['buyer_token']}"
        }
    )

    request_id = create_response.json()["id"]

    response = client.patch(
        f"/api/purchase-requests/{request_id}/status",
        json={"status": "rejected"},
        headers={
            "Authorization": f"Bearer {data['seller_token']}"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


# --------------------------------------------------
# Test 11: Cannot update an already accepted request
# --------------------------------------------------

def test_cannot_update_already_accepted_request(client, purchase_test_data):

    data = purchase_test_data

    create_response = client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={"message": "Interested"},
        headers={
            "Authorization": f"Bearer {data['buyer_token']}"
        }
    )

    request_id = create_response.json()["id"]

    headers = {
        "Authorization": f"Bearer {data['seller_token']}"
    }

    first_response = client.patch(
        f"/api/purchase-requests/{request_id}/status",
        json={"status": "accepted"},
        headers=headers
    )

    assert first_response.status_code == 200

    second_response = client.patch(
        f"/api/purchase-requests/{request_id}/status",
        json={"status": "rejected"},
        headers=headers
    )

    assert second_response.status_code == 400


# --------------------------------------------------
# Test 12: Unauthorized user cannot send a request
# --------------------------------------------------

def test_unauthorized_user_cannot_send_request(client, purchase_test_data):

    data = purchase_test_data

    response = client.post(
        f"/api/purchase-requests/{data['mobile_id']}",
        json={"message": "Interested"}
    )

    assert response.status_code == 401