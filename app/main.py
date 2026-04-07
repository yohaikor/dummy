from __future__ import annotations

from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates





OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=37.7749&longitude=-122.4194&current_weather=true"
)

CITY_NAME = "San Francisco"

templates = Jinja2Templates(directory="templates")

app = FastAPI(title="Vibeline Guinea Pig", version="0.1.0")


def weathercode_to_vibe(code: int) -> str:
    if code == 0:
        return "crystal clear"
    if code in (1, 2):
        return "soft skies"
    if code == 3:
        return "overcast introspection"
    if code in (45, 48):
        return "foggy mystery"
    if code in (51, 53, 55, 56, 57):
        return "drizzly comfort"
    if code in (61, 63, 65, 66, 67):
        return "rainy focus"
    if code in (71, 73, 75, 77):
        return "snowy hush"
    if code in (80, 81, 82):
        return "showers and momentum"
    if code in (85, 86):
        return "snowy bursts"
    if code in (95, 96, 99):
        return "storm energy"
    return "unclassified vibe"


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    render_time = datetime.now(timezone.utc).isoformat(timespec="seconds")

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            resp = await client.get(OPEN_METEO_URL)
            resp.raise_for_status()
            data = resp.json()

        current = data.get("current_weather") or {}
        temperature_c = current.get("temperature")
        wind_kph = current.get("windspeed")
        weather_code = current.get("weathercode")
        weather_time = current.get("time")

        if (
            temperature_c is None
            or wind_kph is None
            or weather_code is None
            or weather_time is None
        ):
            raise ValueError("unexpected Open-Meteo response shape")

        vibe = weathercode_to_vibe(int(weather_code))

        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "city_name": CITY_NAME,
                "temperature_c": temperature_c,
                "wind_kph": wind_kph,
                "vibe": vibe,
                "weather_time": weather_time,
                "render_time": render_time,
                "error": None,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "city_name": CITY_NAME,
                "temperature_c": None,
                "wind_kph": None,
                "vibe": None,
                "weather_time": None,
                "render_time": render_time,
                "error": str(exc),
            },
            status_code=200,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
