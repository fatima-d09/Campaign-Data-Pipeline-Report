import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.open.fec.gov/v1"


def get_api_key():
    key = os.getenv("FEC_API_KEY")
    if not key:
        raise RuntimeError("FEC_API_KEY not found in environment")
    return key


def fec_get(path, params=None):
    if params is None:
        params = {}

    params["api_key"] = get_api_key()
    url = f"{BASE_URL}{path}"

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

