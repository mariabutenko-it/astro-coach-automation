import requests

from config.settings import API_URL, API_TOKEN


class APIClient:

    def __init__(self, base_url=API_URL):
        self.base_url = base_url

    def get(self, endpoint):
        url = f"{self.base_url}{endpoint}"

        headers = {}

        if API_TOKEN:
            headers["Authorization"] = f"Bearer {API_TOKEN}"

        response = requests.get(
            url,
            headers=headers
        )

        return response

    def post(self, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"

        headers = {}

        if API_TOKEN:
            headers["Authorization"] = f"Bearer {API_TOKEN}"

        response = requests.post(
            url,
            json=data,
            headers=headers
        )

        return response
