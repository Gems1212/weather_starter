from dataclasses import dataclass

import httpx


class WeatherProviderError(Exception):
    pass


@dataclass
class SingaporeWeatherClient:
    base_url: str = "https://api-open.data.gov.sg"
    two_hour_path: str = "/v2/real-time/api/two-hr-forecast"
    air_temperature_path: str = "/v2/real-time/api/air-temperature"
    relative_humidity_path: str = "/v2/real-time/api/relative-humidity"
    rainfall_path: str = "/v2/real-time/api/rainfall"
    wind_speed_path: str = "/v2/real-time/api/wind-speed"
    wind_direction_path: str = "/v2/real-time/api/wind-direction"
    forecast_24h_path: str = "/v1/environment/24-hour-weather-forecast"
    forecast_4day_path: str = "/v1/environment/4-day-weather-forecast"
    timeout_seconds: float = 8.0
    user_agent: str = "weather-starter/0.1 (educational project)"
    api_key: str | None = None

    def fetch_latest_forecast_payload(self) -> dict:
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
            return self._fetch_json(client, f"{self.base_url}{self.two_hour_path}")

    def fetch_air_temperature_payload(self) -> dict:
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
            return self._fetch_json(client, f"{self.base_url}{self.air_temperature_path}")

    def fetch_relative_humidity_payload(self) -> dict:
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
            return self._fetch_json(client, f"{self.base_url}{self.relative_humidity_path}")

    def fetch_rainfall_payload(self) -> dict:
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
            return self._fetch_json(client, f"{self.base_url}{self.rainfall_path}")

    def fetch_wind_speed_payload(self) -> dict:
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
            return self._fetch_json(client, f"{self.base_url}{self.wind_speed_path}")

    def fetch_wind_direction_payload(self) -> dict:
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
            return self._fetch_json(client, f"{self.base_url}{self.wind_direction_path}")

    def fetch_24hour_forecast_payload(self) -> dict:
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
            return self._fetch_json(client, f"{self.base_url}{self.forecast_24h_path}")

    def fetch_4day_forecast_payload(self) -> dict:
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
            return self._fetch_json(client, f"{self.base_url}{self.forecast_4day_path}")

    def get_current_weather(self, latitude: float, longitude: float) -> dict:
        payload = self.fetch_latest_forecast_payload()
        return self.snapshot_from_payload(payload, latitude, longitude)

    def get_air_temperature(self, latitude: float, longitude: float) -> dict:
        payload = self.fetch_air_temperature_payload()
        return self.snapshot_air_temperature_payload(payload, latitude, longitude)

    def get_relative_humidity(self, latitude: float, longitude: float) -> dict:
        payload = self.fetch_relative_humidity_payload()
        return self.snapshot_relative_humidity_payload(payload, latitude, longitude)

    def get_rainfall(self, latitude: float, longitude: float) -> dict:
        payload = self.fetch_rainfall_payload()
        return self.snapshot_rainfall_payload(payload, latitude, longitude)

    def get_wind_speed(self, latitude: float, longitude: float) -> dict:
        payload = self.fetch_wind_speed_payload()
        return self.snapshot_wind_speed_payload(payload, latitude, longitude)

    def get_wind_direction(self, latitude: float, longitude: float) -> dict:
        payload = self.fetch_wind_direction_payload()
        return self.snapshot_wind_direction_payload(payload, latitude, longitude)

    def get_24hour_forecast(self, latitude: float, longitude: float) -> dict:
        payload = self.fetch_24hour_forecast_payload()
        return self.snapshot_24hour_forecast_payload(payload, latitude, longitude)

    def get_4day_forecast(self, latitude: float, longitude: float) -> dict:
        payload = self.fetch_4day_forecast_payload()
        return self.snapshot_4day_forecast_payload(payload, latitude, longitude)

    def snapshot_from_payload(self, payload: dict, latitude: float, longitude: float) -> dict:
        if isinstance(payload, dict) and payload.get("code") not in (None, 0):
            message = payload.get("errorMsg") or "Weather provider returned an error"
            raise WeatherProviderError(message)

        data = payload.get("data") if isinstance(payload, dict) else None
        root = data if isinstance(data, dict) else payload

        area_metadata = root.get("area_metadata", [])
        items = root.get("items", [])
        if not items:
            raise WeatherProviderError("Forecast response has no items")

        latest_item = items[0]
        forecasts = latest_item.get("forecasts", [])
        if not forecasts:
            raise WeatherProviderError("Forecast item has no area forecasts")

        forecast_by_area = {
            entry.get("area"): entry.get("forecast")
            for entry in forecasts
            if entry.get("area") and entry.get("forecast")
        }

        nearest_area = self._nearest_area_name(area_metadata, latitude, longitude)
        if nearest_area and nearest_area in forecast_by_area:
            area = nearest_area
            condition = forecast_by_area[nearest_area]
        else:
            fallback = forecasts[0]
            area = fallback.get("area")
            condition = fallback.get("forecast") or "Unknown"

        return {
            "condition": condition,
            "observed_at": latest_item.get("update_timestamp")
            or latest_item.get("timestamp")
            or "",
            "source": "api-open.data.gov.sg",
            "area": area,
            "valid_period_text": latest_item.get("valid_period", {}).get("text"),
        }

    def snapshot_air_temperature_payload(
        self, payload: dict, latitude: float, longitude: float
    ) -> dict:
        if isinstance(payload, dict) and payload.get("code") not in (None, 0):
            message = payload.get("errorMsg") or "Weather provider returned an error"
            raise WeatherProviderError(message)

        data = payload.get("data") if isinstance(payload, dict) else None
        root = data if isinstance(data, dict) else payload

        stations = root.get("stations", [])
        if not stations:
            raise WeatherProviderError("Air temperature response has no stations")

        nearest_station = self._nearest_station(stations, latitude, longitude)
        temperature = nearest_station.get("value") if nearest_station else "Unknown"

        return {
            "temperature": temperature,
            "observed_at": root.get("timestamp") or "",
            "source": "api-open.data.gov.sg",
            "unit": "Celsius",
        }

    def snapshot_relative_humidity_payload(
        self, payload: dict, latitude: float, longitude: float
    ) -> dict:
        if isinstance(payload, dict) and payload.get("code") not in (None, 0):
            message = payload.get("errorMsg") or "Weather provider returned an error"
            raise WeatherProviderError(message)

        data = payload.get("data") if isinstance(payload, dict) else None
        root = data if isinstance(data, dict) else payload

        stations = root.get("stations", [])
        if not stations:
            raise WeatherProviderError("Relative humidity response has no stations")

        nearest_station = self._nearest_station(stations, latitude, longitude)
        humidity = nearest_station.get("value") if nearest_station else "Unknown"

        return {
            "humidity": humidity,
            "observed_at": root.get("timestamp") or "",
            "source": "api-open.data.gov.sg",
            "unit": "Percent",
        }

    def snapshot_rainfall_payload(
        self, payload: dict, latitude: float, longitude: float
    ) -> dict:
        if isinstance(payload, dict) and payload.get("code") not in (None, 0):
            message = payload.get("errorMsg") or "Weather provider returned an error"
            raise WeatherProviderError(message)

        data = payload.get("data") if isinstance(payload, dict) else None
        root = data if isinstance(data, dict) else payload

        stations = root.get("stations", [])
        if not stations:
            raise WeatherProviderError("Rainfall response has no stations")

        nearest_station = self._nearest_station(stations, latitude, longitude)
        rainfall = nearest_station.get("value") if nearest_station else "Unknown"

        return {
            "rainfall": rainfall,
            "observed_at": root.get("timestamp") or "",
            "source": "api-open.data.gov.sg",
            "unit": "Millimeter",
        }

    def snapshot_wind_speed_payload(
        self, payload: dict, latitude: float, longitude: float
    ) -> dict:
        if isinstance(payload, dict) and payload.get("code") not in (None, 0):
            message = payload.get("errorMsg") or "Weather provider returned an error"
            raise WeatherProviderError(message)

        data = payload.get("data") if isinstance(payload, dict) else None
        root = data if isinstance(data, dict) else payload

        stations = root.get("stations", [])
        if not stations:
            raise WeatherProviderError("Wind speed response has no stations")

        nearest_station = self._nearest_station(stations, latitude, longitude)
        wind_speed = nearest_station.get("value") if nearest_station else "Unknown"

        return {
            "wind_speed": wind_speed,
            "observed_at": root.get("timestamp") or "",
            "source": "api-open.data.gov.sg",
            "unit": "Knots",
        }

    def snapshot_wind_direction_payload(
        self, payload: dict, latitude: float, longitude: float
    ) -> dict:
        if isinstance(payload, dict) and payload.get("code") not in (None, 0):
            message = payload.get("errorMsg") or "Weather provider returned an error"
            raise WeatherProviderError(message)

        data = payload.get("data") if isinstance(payload, dict) else None
        root = data if isinstance(data, dict) else payload

        stations = root.get("stations", [])
        if not stations:
            raise WeatherProviderError("Wind direction response has no stations")

        nearest_station = self._nearest_station(stations, latitude, longitude)
        wind_direction = nearest_station.get("value") if nearest_station else "Unknown"

        return {
            "wind_direction": wind_direction,
            "observed_at": root.get("timestamp") or "",
            "source": "api-open.data.gov.sg",
            "unit": "Degrees",
        }

    def snapshot_24hour_forecast_payload(
        self, payload: dict, latitude: float, longitude: float
    ) -> dict:
        if isinstance(payload, dict) and payload.get("code") not in (None, 0):
            message = payload.get("errorMsg") or "Weather provider returned an error"
            raise WeatherProviderError(message)

        data = payload.get("data") if isinstance(payload, dict) else None
        root = data if isinstance(data, dict) else payload

        items = root.get("items", [])
        if not items:
            raise WeatherProviderError("24-hour forecast response has no items")

        latest_item = items[0]
        periods = latest_item.get("periods", [])
        if not periods:
            raise WeatherProviderError("24-hour forecast item has no periods")

        # Return the first period as a representative forecast
        first_period = periods[0]
        condition = first_period.get("forecast", "Unknown")

        return {
            "condition": condition,
            "observed_at": root.get("update_timestamp") or root.get("timestamp") or "",
            "source": "api-open.data.gov.sg",
            "forecast_type": "24-hour",
            "periods_count": len(periods),
        }

    def snapshot_4day_forecast_payload(
        self, payload: dict, latitude: float, longitude: float
    ) -> dict:
        if isinstance(payload, dict) and payload.get("code") not in (None, 0):
            message = payload.get("errorMsg") or "Weather provider returned an error"
            raise WeatherProviderError(message)

        data = payload.get("data") if isinstance(payload, dict) else None
        root = data if isinstance(data, dict) else payload

        items = root.get("items", [])
        if not items:
            raise WeatherProviderError("4-day forecast response has no items")

        latest_item = items[0]
        forecasts = latest_item.get("forecasts", [])
        if not forecasts:
            raise WeatherProviderError("4-day forecast item has no forecasts")

        # Return the first day as a representative forecast
        first_forecast = forecasts[0]
        condition = first_forecast.get("forecast", "Unknown")

        return {
            "condition": condition,
            "observed_at": root.get("update_timestamp") or root.get("timestamp") or "",
            "source": "api-open.data.gov.sg",
            "forecast_type": "4-day",
            "forecasts_count": len(forecasts),
        }

    @staticmethod
    def _fetch_json(client: httpx.Client, url: str) -> dict:
        try:
            response = client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code == 429:
                raise WeatherProviderError(
                    "Weather provider rate limit reached (HTTP 429)"
                ) from exc
            if status_code in (401, 403):
                raise WeatherProviderError(
                    "Weather provider rejected request (check API key)"
                ) from exc
            raise WeatherProviderError(f"Weather provider returned HTTP {status_code}") from exc
        except httpx.HTTPError as exc:
            raise WeatherProviderError("Unable to reach weather provider") from exc

    @staticmethod
    def _nearest_area_name(
        area_metadata: list[dict], latitude: float, longitude: float
    ) -> str | None:
        nearest_name: str | None = None
        nearest_distance: float | None = None

        for area in area_metadata:
            label = area.get("label_location", {})
            lat = label.get("latitude")
            lon = label.get("longitude")
            name = area.get("name")
            if lat is None or lon is None or not name:
                continue

            delta = (float(lat) - latitude) ** 2 + (float(lon) - longitude) ** 2
            if nearest_distance is None or delta < nearest_distance:
                nearest_distance = delta
                nearest_name = name

        return nearest_name

    @staticmethod
    def _nearest_station(
        stations: list[dict], latitude: float, longitude: float
    ) -> dict | None:
        nearest_station: dict | None = None
        nearest_distance: float | None = None

        for station in stations:
            location = station.get("location", {})
            lat = location.get("latitude")
            lon = location.get("longitude")
            if lat is None or lon is None:
                continue

            delta = (float(lat) - latitude) ** 2 + (float(lon) - longitude) ** 2
            if nearest_distance is None or delta < nearest_distance:
                nearest_distance = delta
                nearest_station = station

        return nearest_station
