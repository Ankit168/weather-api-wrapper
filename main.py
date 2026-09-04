from fastapi import FastAPI,HTTPException,status
import os
import httpx
from dotenv import load_dotenv
from typing import Literal
import json,redis
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

redis_client = redis.Redis(host="localhost",
                           port=6379,
                           decode_responses=True)
app = FastAPI()

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

@app.get("/weather")
@limiter.limit("10/minute")
def get_weather(request:Request,city: str,unit:Literal["celsius","fahrenheit"] = "celsius"):
    openweather_units = {"celsius":"metric",
                         "fahrenheit":"imperial"}

    query_params = { "q" : city,
                    "appid" : API_KEY,
                    "units" : openweather_units[unit]
    }
    cache_key = f"weather:{city.lower()}:{unit}"
    cached_weather = redis_client.get(cache_key)
    if cached_weather:
        return json.loads(cached_weather)

    try:

        response = httpx.get("https://api.openweathermap.org/data/2.5/weather",params=query_params)
        response.raise_for_status()
        data = response.json()
        result = { "city" : data["name"],
            "temperature" : data["main"]["temp"],
            "unit" : unit,
            "condition": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        }
        redis_client.setex(
            cache_key,
            60*60*12,
            json.dumps(result)
        )

        return result
    
    except httpx.HTTPStatusError as exc:
        err_message = exc.response.json().get("message","OpenWeatherMap API error")
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Weather API Error: {err_message}"
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code= status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = "Weather service is temporary unvailable.Please try again after sometime!"
        )
    
