import pytest

from pages.example_page import ExamplePage


@pytest.mark.ui
def test_example_page(page):
    example_page = ExamplePage(page)

    example_page.open()

    assert example_page.get_title() == "Example Domain"
