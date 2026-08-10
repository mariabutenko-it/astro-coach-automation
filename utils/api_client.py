import requests

from config.settings import API_URL, API_TOKEN


class APIClient:

    def __init__(self, base_url=API_URL):
        self.base_url = base_url

    def get(self, endpoint):
        url = f"{self.base_url}{endpoint}"

        headers = {
            "Accept": "application/json"
        }

        if API_TOKEN:
            headers["Authorization"] = f"Bearer {API_TOKEN}"

        response = requests.get(
            url,
            headers=headers
        )

        return response

    def get_json(self, endpoint):
        response = self.get(endpoint)

        return response.json()

    def post(self, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if API_TOKEN:
            headers["Authorization"] = f"Bearer {API_TOKEN}"

        response = requests.post(
            url,
            json=data,
            headers=headers
        )

        return response
