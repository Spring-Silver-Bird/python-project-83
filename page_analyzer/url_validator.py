#!/usr/bin/env python3
import validators
from urllib.parse import urlparse



def normalize_url(url: str) -> str:
    """Normalize URL by keeping protocol and path"""
    parsed_url = urlparse(url)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.hostname}"
    print(f'Normalize URL: {normalized_url}')
    return normalized_url

def validate_url(url: str) -> bool:
    """Validate URL format"""
    errors = {}

    if not validators.url(url):
        errors['url'] = 'Некорректный формат URL'
    if url == "":
        errors['url'] = 'URL не может быть пустым'
    if len(url) > 255:
        errors['url'] = 'Слишком длинный URL (должен быть короче 255 символов)'

    return errors
