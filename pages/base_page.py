from config import settings


class BasePage:

    def __init__(self, page):
        self.page = page

    def open(self, path=""):
        self.page.goto(
            f"{settings.BASE_URL}{path}"
        )

    def get_title(self):

        return self.page.title()
