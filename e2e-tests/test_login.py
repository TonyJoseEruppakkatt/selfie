
import os

from playwright.sync_api import expect


TEST_EMAIL = os.getenv("SELFIE_TEST_EMAIL")
TEST_PASSWORD = os.getenv("SELFIE_TEST_PASSWORD")


def test_existing_user_can_login(page, frontend_url):
    assert TEST_EMAIL, "Set SELFIE_TEST_EMAIL environment variable"
    assert TEST_PASSWORD, "Set SELFIE_TEST_PASSWORD environment variable"

    page.goto(f"{frontend_url}/login")

    page.locator('input[type="email"]').fill(TEST_EMAIL)
    page.locator('input[type="password"]').fill(TEST_PASSWORD)

    page.get_by_role("button", name="Login").click()

    # Wait for successful login and dashboard navigation.
    page.wait_for_url("**/dashboard")

    expect(page).to_have_url(f"{frontend_url}/dashboard")
