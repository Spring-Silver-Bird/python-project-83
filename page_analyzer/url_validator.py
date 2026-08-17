#!/usr/bin/env python3
from urllib.parse import urlparse

import validators

MAX_URL_LENGTH = 255


def normalize_url(url: str) -> str:
    """Normalize URL by keeping protocol and path"""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.hostname}"


def validate_url(url: str) -> bool:
    """Validate URL format"""
    errors = {}

    if not validators.url(url):
        errors['url'] = 'Некорректный формат URL'
    if url == "":
        errors['url'] = 'URL не может быть пустым'
    if len(url) > MAX_URL_LENGTH:
        errors['url'] = 'Слишком длинный URL (должен быть короче 255 символов)'

    return errors
