from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

client = TestClient(app)


def test_missing_city_returns_422():
    response = client.get("/weather")

    assert response.status_code == 422


def test_invalid_unit_returns_422():
    response = client.get(
        "/weather",
        params={
            "city": "Mumbai",
            "unit": "kelvin",
        },
    )

    assert response.status_code == 422

def test_weather_response_is_cleaned():
    provider_response = Mock()
    provider_response.json.return_value = {
        "name": "Mumbai",
        "main": {
            "temp": 29.5,
            "humidity": 74,
        },
        "weather": [
            {
                "description": "haze",
            }
        ],
    }

    with (
        patch("main.redis_client.get", return_value=None),
        patch("main.redis_client.setex"),
        patch("main.httpx.get", return_value=provider_response),
    ):
        response = client.get(
            "/weather",
            params={"city": "Mumbai"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "city": "Mumbai",
        "temperature": 29.5,
        "unit": "celsius",
        "condition": "haze",
        "humidity": 74,
    }