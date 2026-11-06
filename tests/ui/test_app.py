import pytest
from playwright.sync_api import Page, expect

def test_app_loads(page: Page):
    page.goto("http://localhost:8501")
    expect(page.locator("h1")).to_contain_text("AI Resume Screener")
