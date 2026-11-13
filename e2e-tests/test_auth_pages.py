
def test_login_page_loads(page, frontend_url):
    response = page.goto(f"{frontend_url}/login")

    assert response is not None
    assert response.status == 200

    assert page.locator("form").is_visible()


def test_register_page_loads(page, frontend_url):
    response = page.goto(f"{frontend_url}/register")

    assert response is not None
    assert response.status == 200

    assert page.locator("form").is_visible()
