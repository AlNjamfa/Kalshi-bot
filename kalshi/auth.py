import os
import time
import base64
import requests
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

load_dotenv()

KALSHI_API_URL = "https://api.elections.kalshi.com/trade-api/v2"
KEY_ID = os.getenv("KALSHI_KEY_ID")
PRIVATE_KEY_PATH = os.getenv("KALSHI_PRIVATE_KEY_PATH")

def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        key_data = f.read()
    try:
        return serialization.load_pem_private_key(
            key_data, password=None, backend=default_backend()
        )
    except Exception:
        return serialization.load_der_private_key(
            key_data, password=None, backend=default_backend()
        )

def sign_request(method, path):
    timestamp = str(int(time.time() * 1000))
    message = timestamp + method.upper() + path
    private_key = load_private_key()
    signature = private_key.sign(
        message.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH
        ),
        hashes.SHA256()
    )
    return timestamp, base64.b64encode(signature).decode("utf-8")

def get_auth_headers(method, path):
    timestamp, signature = sign_request(method, path)
    return {
        "KALSHI-ACCESS-KEY": KEY_ID,
        "KALSHI-ACCESS-TIMESTAMP": timestamp,
        "KALSHI-ACCESS-SIGNATURE": signature,
        "Content-Type": "application/json"
    }

def get_balance():
    path = "/trade-api/v2/portfolio/balance"
    headers = get_auth_headers("GET", path)
    r = requests.get(f"{KALSHI_API_URL}/portfolio/balance", headers=headers)
    return r.json()
