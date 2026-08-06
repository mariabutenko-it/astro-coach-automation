from playwright.sync_api import Page


class ExamplePage:
    def __init__(self, page: Page):
        self.page = page

    def open(self):
        self.page.goto("https://example.com")

    def get_title(self):
        return self.page.title()
