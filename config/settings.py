import os

from dotenv import load_dotenv

load_dotenv()


ENV = os.getenv("ENV", "local")

BASE_URL = os.getenv(
    "BASE_URL",
    "https://example.com"
)

API_URL = os.getenv(
    "API_URL",
    "https://dev.api.astro-c.com"
)

USERNAME = os.getenv(
    "USERNAME",
    ""
)

PASSWORD = os.getenv(
    "PASSWORD",
    ""
)

API_TOKEN = os.getenv(
    "API_TOKEN",
    ""
)
