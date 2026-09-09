"""
geocoding_service.py — real, keyless geocoding + weather lookup for the
Savings Estimator.

No API key is configured anywhere in this project, so this uses two free,
keyless public services rather than blocking the feature on an API key you
don't have yet:

  - Nominatim (OpenStreetMap) for address -> lat/lon geocoding and
    autocomplete suggestions. Usage policy requires a descriptive
    User-Agent and reasonable rate limits (we do not cache/hammer it).
    https://operations.osmfoundation.org/policies/nominatim/
  - Open-Meteo for current weather at a given lat/lon. This is already one
    of Circuit Saver's documented data sources (cited in the project
    overview as a grid-intelligence integration for the real baseline
    model), so using it here is consistent with the existing architecture,
    not a new dependency invented for this feature.

Both are called synchronously with short timeouts; if either is
unreachable (no internet, rate-limited, etc.), callers fall back to the
non-location-aware estimate rather than failing the whole request.
"""

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
USER_AGENT = "CircuitSaver-SavingsEstimator/1.0 (congressional app challenge student project)"


def autocomplete_address(query: str, limit: int = 5) -> list[dict]:
    if not query or len(query.strip()) < 3:
        return []
    try:
        resp = httpx.get(
            NOMINATIM_URL,
            params={"q": query, "format": "jsonv2", "limit": limit, "addressdetails": 1},
            headers={"User-Agent": USER_AGENT},
            timeout=4.0,
        )
        resp.raise_for_status()
        results = resp.json()
    except Exception:
        return []

    return [
        {
            "display_name": r.get("display_name"),
            "lat": float(r["lat"]),
            "lon": float(r["lon"]),
            "country_code": (r.get("address") or {}).get("country_code"),
        }
        for r in results
        if "lat" in r and "lon" in r
    ]


def geocode_single(address: str) -> dict | None:
    matches = autocomplete_address(address, limit=1)
    return matches[0] if matches else None


def get_current_temperature_c(lat: float, lon: float) -> float | None:
    try:
        resp = httpx.get(
            OPEN_METEO_URL,
            params={"latitude": lat, "longitude": lon, "current_weather": "true"},
            timeout=4.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("current_weather", {}).get("temperature")
    except Exception:
        return None
