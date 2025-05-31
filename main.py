from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("2C92ASCcTspGD63sr03JDGGfQ5XZ2reG")
BASE_URL = "https://dataservice.accuweather.com"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OpenAI GPT-friendly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/weather")
async def get_weather(city: str = Query(..., description="City name like 'St. John's'")):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")

    async with httpx.AsyncClient() as client:
        # Step 1: Get the location key for the city
        location_res = await client.get(
            f"{BASE_URL}/locations/v1/cities/search",
            params={"apikey": API_KEY, "q": city}
        )
        if location_res.status_code != 200 or not location_res.json():
            raise HTTPException(status_code=404, detail="City not found")
        location_key = location_res.json()[0]["Key"]

        # Step 2: Get current weather for that location
        weather_res = await client.get(
            f"{BASE_URL}/currentconditions/v1/{location_key}",
            params={"apikey": API_KEY}
        )
        if weather_res.status_code != 200 or not weather_res.json():
            raise HTTPException(status_code=500, detail="Weather data unavailable")

        return weather_res.json()[0]  # Return the first (and usually only) condition object
