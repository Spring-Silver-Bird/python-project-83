import requests

from page_analyzer.api_utils import (
    fetch_url,
    handle_api_error,
    handle_request_error,
)


def test_handle_request_error_timeout():
    error = requests.Timeout("timed out")
    assert handle_request_error(error) == "Превышено время ожидания запроса"


def test_handle_api_error_connection_error():
    error = requests.ConnectionError("connection failed")
    assert handle_api_error(error) == "Не удалось установить соединение с API"


def test_fetch_url_returns_error_message(monkeypatch):
    def fake_get(url, timeout=5):  # noqa: ARG001
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(requests, "get", fake_get)

    response, error = fetch_url("https://example.com")

    assert response is None
    assert error == "Не удалось установить соединение с API"
