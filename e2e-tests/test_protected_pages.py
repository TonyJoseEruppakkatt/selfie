
import os
from playwright.sync_api import expect

TEST_EMAIL = os.getenv("SELFIE_TEST_EMAIL")
TEST_PASSWORD = os.getenv("SELFIE_TEST_PASSWORD")


PROTECTED_ROUTES = [
    "/dashboard",
    "/sell",
    "/my-listings",
    "/buyer-requests",
    "/seller-requests",
]


def test_unauthenticated_user_redirected_to_login(
    page,
    frontend_url
):
    for route in PROTECTED_ROUTES:
        page.goto(f"{frontend_url}{route}")

        # Protected pages should redirect to login.
        page.wait_for_url("**/login")

        expect(
            page.locator('input[type="email"]')
        ).to_be_visible()


def test_logged_in_user_can_access_protected_pages(
    page,
    frontend_url
):
    assert TEST_EMAIL, "Set SELFIE_TEST_EMAIL environment variable"
    assert TEST_PASSWORD, "Set SELFIE_TEST_PASSWORD environment variable"

    # Login using the existing user account.
    page.goto(f"{frontend_url}/login")

    page.locator('input[type="email"]').fill(TEST_EMAIL)
    page.locator('input[type="password"]').fill(TEST_PASSWORD)

    page.get_by_role("button", name="Login").click()

    # Wait until login is completed.
    page.wait_for_function(
        "() => localStorage.getItem('access_token') !== null"
    )

    # Open each protected page.
    for route in PROTECTED_ROUTES:
        page.goto(f"{frontend_url}{route}")

        expect(page).to_have_url(
            f"{frontend_url}{route}"
        )

        expect(page.locator("body")).to_be_visible()
