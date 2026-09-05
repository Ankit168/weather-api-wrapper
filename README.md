# Weather API Wrapper Service

A FastAPI service that fetches current weather data from OpenWeatherMap.

## Features

- Get current weather by city
- Celsius and Fahrenheit support
- Redis caching for 12 hours
- Rate limiting: 10 requests per minute per IP address
- Input and provider-error handling
- Interactive API documentation at `/docs`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENWEATHER_API_KEY=your_openweather_api_key
```

Start Redis:

```bash
brew services start redis
```

Run the API:

```bash
uvicorn main:app --reload
```

## Usage

Open interactive documentation:

```text
http://127.0.0.1:8000/docs
https://weather-api-wrapper-yroh.onrender.com/
```

Example requests:

```text
http://127.0.0.1:8000/weather?city=Mumbai
http://127.0.0.1:8000/weather?city=Mumbai&unit=fahrenheit
```

Example response:

```json
{
  "city": "Mumbai",
  "temperature": 29.5,
  "unit": "celsius",
  "condition": "haze",
  "humidity": 74
}
```
