"""Rate-limited Figma file retrieval; secrets live only in environment."""
import re
import requests
from .core import MAX_BYTES

FILE_KEY = re.compile(r"^[a-zA-Z0-9]{8,128}$")


def fetch_figma_file(file_key, token, *, timeout=30, session=None):
    if not FILE_KEY.fullmatch(file_key):
        raise ValueError("Invalid Figma file key")
    if not token:
        raise ValueError("FIGMA_TOKEN must be configured")
    client = session or requests
    # Host is fixed; never accept arbitrary URLs from user input.
    response = client.get(
        f"https://api.figma.com/v1/files/{file_key}",
        headers={"X-Figma-Token": token},
        timeout=timeout,
        stream=True,
        allow_redirects=False,
    )
    if response.status_code != 200:
        raise ValueError(f"Figma API returned HTTP {response.status_code}")
    length = response.headers.get("Content-Length")
    if length and int(length) > MAX_BYTES:
        raise ValueError("Figma response too large")
    raw = bytearray()
    try:
        for chunk in response.iter_content(65536):
            raw.extend(chunk)
            if len(raw) > MAX_BYTES:
                raise ValueError("Figma response too large")
        document = __import__("json").loads(raw)
    finally:
        response.close()
    if not isinstance(document, dict):
        raise ValueError("Invalid Figma API response")
    return document
