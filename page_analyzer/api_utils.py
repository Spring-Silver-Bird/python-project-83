import requests


def handle_request_error(error):
    if isinstance(error, requests.Timeout):
        return "Превышено время ожидания запроса"
    if isinstance(error, requests.ConnectionError):
        return "Не удалось установить соединение с API"
    return "Произошла ошибка при запросе к API"


def handle_api_error(error):
    return handle_request_error(error)


def fetch_url(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response, None
    except requests.RequestException as error:
        return None, handle_api_error(error)
