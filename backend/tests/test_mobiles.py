
import pytest


# --------------------------------------------------
# Helper: Register and login a user
# --------------------------------------------------

def register_and_login(client, name, email, phone):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": name,
            "email": email,
            "phone_number": phone,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


# --------------------------------------------------
# Helper: Create a mobile listing
# --------------------------------------------------

def create_listing(client, token, brand="Samsung", model="Galaxy S24",
                   price="25000", condition="Excellent"):

    return client.post(
        "/api/mobiles",
        data={
            "brand": brand,
            "model": model,
            "price": price,
            "condition": condition,
            "description": "Test mobile listing",
        },
        files=[
            (
                "images",
                ("mobile.jpg", b"fake-image-content", "image/jpeg"),
            )
        ],
        headers={
            "Authorization": f"Bearer {token}",
        },
    )


# --------------------------------------------------
# Fixture: Prepare seller, buyer and mobile listing
# --------------------------------------------------

@pytest.fixture
def mobile_test_data(client, monkeypatch):

    # Fake Cloudinary upload
    def fake_upload(image_content):
        return {
            "image_url": "https://res.cloudinary.com/demo/image/upload/test.jpg",
            "public_id": "test_mobile_image",
        }

    # Fake Cloudinary deletion
    deleted_images = []

    def fake_delete(public_id):
        deleted_images.append(public_id)
        return True

    monkeypatch.setattr(
        "app.services.mobile_service.upload_mobile_image",
        fake_upload,
    )

    monkeypatch.setattr(
        "app.services.mobile_service.delete_mobile_image",
        fake_delete,
    )

    # Register seller
    seller_token = register_and_login(
        client,
        "Test Seller",
        "mobile_seller@test.com",
        "9876543210",
    )

    # Register another user
    buyer_token = register_and_login(
        client,
        "Test Buyer",
        "mobile_buyer@test.com",
        "9876543211",
    )

    # Create a mobile listing
    create_response = create_listing(
        client,
        seller_token,
    )

    assert create_response.status_code == 201

    mobile_id = create_response.json()["id"]

    return {
        "seller_token": seller_token,
        "buyer_token": buyer_token,
        "mobile_id": mobile_id,
        "deleted_images": deleted_images,
    }


# --------------------------------------------------
# Test 1: Create mobile listing
# --------------------------------------------------

def test_create_mobile_listing(client, mobile_test_data):

    data = mobile_test_data

    response = create_listing(
        client,
        data["seller_token"],
        brand="Apple",
        model="iPhone 15",
        price="45000",
        condition="Like New",
    )

    assert response.status_code == 201

    result = response.json()

    assert result["brand"] == "Apple"
    assert result["model"] == "iPhone 15"
    assert result["status"] == "available"
    assert len(result["images"]) == 1


# --------------------------------------------------
# Test 2: Get all mobile listings
# --------------------------------------------------

def test_get_mobile_listings(client, mobile_test_data):

    response = client.get("/api/mobiles")

    assert response.status_code == 200

    result = response.json()

    assert result["total"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["brand"] == "Samsung"


# --------------------------------------------------
# Test 3: Get mobile details
# --------------------------------------------------

def test_get_mobile_details(client, mobile_test_data):

    mobile_id = mobile_test_data["mobile_id"]

    response = client.get(
        f"/api/mobiles/{mobile_id}"
    )

    assert response.status_code == 200

    result = response.json()

    assert result["id"] == mobile_id
    assert result["brand"] == "Samsung"
    assert result["model"] == "Galaxy S24"
    assert len(result["images"]) == 1


# --------------------------------------------------
# Test 4: Search mobile by brand or model
# --------------------------------------------------

def test_search_mobile(client, mobile_test_data):

    response = client.get(
        "/api/mobiles",
        params={"search": "Samsung"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = client.get(
        "/api/mobiles",
        params={"search": "Galaxy"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1


# --------------------------------------------------
# Test 5: Filter mobile by price
# --------------------------------------------------

def test_filter_mobile_by_price(client, mobile_test_data):

    response = client.get(
        "/api/mobiles",
        params={
            "min_price": 20000,
            "max_price": 30000,
        },
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = client.get(
        "/api/mobiles",
        params={
            "min_price": 30000,
            "max_price": 40000,
        },
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0


# --------------------------------------------------
# Test 6: Filter mobile by condition
# --------------------------------------------------

def test_filter_mobile_by_condition(client, mobile_test_data):

    response = client.get(
        "/api/mobiles",
        params={"condition": "Excellent"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = client.get(
        "/api/mobiles",
        params={"condition": "Good"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0


# --------------------------------------------------
# Test 7: Update mobile listing
# --------------------------------------------------

def test_update_mobile_listing(client, mobile_test_data):

    data = mobile_test_data

    response = client.put(
        f"/api/mobiles/{data['mobile_id']}",
        data={
            "brand": "Samsung",
            "model": "Galaxy S24 Ultra",
            "price": "35000",
        },
        headers={
            "Authorization": f"Bearer {data['seller_token']}",
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["model"] == "Galaxy S24 Ultra"
    assert float(result["price"]) == 35000


# --------------------------------------------------
# Test 8: Another seller cannot update the listing
# --------------------------------------------------

def test_cannot_update_another_sellers_mobile(
    client,
    mobile_test_data,
):

    data = mobile_test_data

    response = client.put(
        f"/api/mobiles/{data['mobile_id']}",
        data={
            "model": "Updated Model",
        },
        headers={
            "Authorization": f"Bearer {data['buyer_token']}",
        },
    )

    assert response.status_code == 403


# --------------------------------------------------
# Test 9: Delete mobile listing
# --------------------------------------------------

def test_delete_mobile_listing(client, mobile_test_data):

    data = mobile_test_data

    response = client.delete(
        f"/api/mobiles/{data['mobile_id']}",
        headers={
            "Authorization": f"Bearer {data['seller_token']}",
        },
    )

    assert response.status_code == 200

    assert response.json()["message"] == (
        "Mobile listing removed successfully"
    )

    assert "test_mobile_image" in data["deleted_images"]

    # Soft-deleted listing should not appear in public listings
    listing_response = client.get("/api/mobiles")

    assert listing_response.status_code == 200
    assert listing_response.json()["total"] == 0


# --------------------------------------------------
# Test 10: Cannot create listing without login
# --------------------------------------------------

def test_cannot_create_mobile_without_login(client):

    response = client.post(
        "/api/mobiles",
        data={
            "brand": "Samsung",
            "model": "Galaxy S24",
            "price": "25000",
            "condition": "Excellent",
        },
        files=[
            (
                "images",
                ("mobile.jpg", b"fake-image-content", "image/jpeg"),
            )
        ],
    )

    assert response.status_code == 401


# --------------------------------------------------
# Test 11: Invalid image format
# --------------------------------------------------

def test_reject_invalid_image_format(client, mobile_test_data):

    data = mobile_test_data

    response = client.post(
        "/api/mobiles",
        data={
            "brand": "Apple",
            "model": "iPhone 15",
            "price": "45000",
            "condition": "Like New",
        },
        files=[
            (
                "images",
                ("document.pdf", b"fake-pdf-content", "application/pdf"),
            )
        ],
        headers={
            "Authorization": f"Bearer {data['seller_token']}",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Only JPEG, PNG and WEBP images are allowed"
    )


# --------------------------------------------------
# Test 12: Invalid mobile condition
# --------------------------------------------------

def test_reject_invalid_mobile_condition(client, mobile_test_data):

    data = mobile_test_data

    response = client.post(
        "/api/mobiles",
        data={
            "brand": "Apple",
            "model": "iPhone 15",
            "price": "45000",
            "condition": "Damaged",
        },
        files=[
            (
                "images",
                ("mobile.jpg", b"fake-image-content", "image/jpeg"),
            )
        ],
        headers={
            "Authorization": f"Bearer {data['seller_token']}",
        },
    )

    assert response.status_code == 400
    assert "Invalid condition" in response.json()["detail"]
