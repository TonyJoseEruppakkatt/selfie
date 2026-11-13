
from playwright.sync_api import expect


def test_homepage_loads(page, frontend_url):
    page.goto(frontend_url)

    # Check that the page has loaded.
    expect(page.locator("body")).to_be_visible()

    # Check that the page title is not empty.
    assert page.title().strip() != ""


def test_mobile_listings_api_returns_success(page, backend_url):
    response = page.request.get(
        f"{backend_url}/api/mobiles"
    )

    assert response.status == 200

    data = response.json()

    # The API should return a list of mobile listings.
    assert "items" in data
    assert isinstance(data["items"], list)
