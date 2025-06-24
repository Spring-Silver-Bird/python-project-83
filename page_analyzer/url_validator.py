import validators
from urllib.parse import urlparse


def validate_and_normalize_url(url):
    """Validates and normalizes a URL."""
    if not url:
        raise ValueError("URL обязателен")

    if len(url) > 255:
        raise ValueError("URL превышает 255 символов")

    if not validators.url(url):
        raise ValueError("Некорректный URL")

    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"