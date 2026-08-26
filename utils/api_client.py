import requests

from config.settings import API_URL, API_TOKEN


class APIClient:

    def __init__(self, base_url=API_URL):
        self.base_url = base_url
        self.access_token = API_TOKEN or None
        self.refresh_token = None

    def _headers(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        return headers

    def get(self, endpoint):
        url = f"{self.base_url}{endpoint}"

        response = requests.get(
            url,
            headers=self._headers()
        )

        return response

    def get_json(self, endpoint):
        response = self.get(endpoint)
        return response.json()

    def post(self, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"

        response = requests.post(
            url,
            json=data,
            headers=self._headers()
        )

        return response

    def save_tokens(self, response):
        response_data = response.json()

        tokens = response_data["data"]["tokens"]

        self.access_token = tokens["accessToken"]
        self.refresh_token = tokens["refreshToken"]

        return tokens
