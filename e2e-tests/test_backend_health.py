
def test_backend_health(page, backend_url):
    response = page.request.get(
        f"{backend_url}/health"
    )

    assert response.status == 200

    data = response.json()

    assert data is not None
