import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--lang=fr-FR",
                "--disable-features=Translate"
            ]
            )
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context(
        locale="fr-FR",
        extra_http_headers={
            "Accept-Language": "fr-FR,fr;q=0.9"
        }
    )
    page = context.new_page()
    yield page
    page.close()
    context.close()
    