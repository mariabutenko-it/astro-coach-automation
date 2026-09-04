import requests

from config.settings import API_TOKEN, API_URL


class APIClient:
    def __init__(self, base_url=API_URL, timeout=15):
        self.base_url = base_url
        self.timeout = timeout
        self.access_token = API_TOKEN or None
        self.refresh_token = None

    def _headers(self, headers=None):
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.access_token:
            request_headers["Authorization"] = f"Bearer {self.access_token}"

        if headers:
            request_headers.update(headers)

        return request_headers

    def get(self, endpoint, headers=None):
        url = f"{self.base_url}{endpoint}"

        response = requests.get(
            url,
            headers=self._headers(headers),
            timeout=self.timeout,
        )

        return response

    def get_json(self, endpoint):
        response = self.get(endpoint)
        return response.json()

    def post(self, endpoint, data=None, headers=None):
        url = f"{self.base_url}{endpoint}"

        response = requests.post(
            url,
            json=data,
            headers=self._headers(headers),
            timeout=self.timeout,
        )

        return response

    def patch(self, endpoint, data=None, headers=None):
        url = f"{self.base_url}{endpoint}"

        response = requests.patch(
            url,
            json=data,
            headers=self._headers(headers),
            timeout=self.timeout,
        )

        return response

    def put(self, endpoint, data=None, headers=None):
        url = f"{self.base_url}{endpoint}"

        response = requests.put(
            url,
            json=data,
            headers=self._headers(headers),
            timeout=self.timeout,
        )

        return response

    def save_tokens(self, response):
        response_data = response.json()

        tokens = response_data["data"]["tokens"]

        self.access_token = tokens["accessToken"]
        self.refresh_token = tokens["refreshToken"]

        return tokens
