from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation

import httpx

from app.core.config import settings
from app.integrations.errors import DataProviderError
from app.integrations.schemas import MacroObservation, MacroSeriesResponse


class FREDProvider:
    """Adapter for the Federal Reserve Bank of St. Louis FRED observations API."""

    provider_name = "fred"
    endpoint = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(
        self,
        api_key: str | None = None,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 10.0,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.fred_api_key
        self._http_client = http_client
        self._timeout = timeout

    async def get_series(
        self,
        series_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> MacroSeriesResponse:
        if not self._api_key:
            raise DataProviderError("FRED_API_KEY is not configured.")
        if not series_id.strip():
            raise ValueError("FRED series_id cannot be empty.")
        today = datetime.now(UTC).date()
        end = end_date or today
        start = start_date or (end - timedelta(days=365))
        if start > end:
            raise ValueError("start_date must be on or before end_date.")

        params: dict[str, str] = {
            "series_id": series_id,
            "api_key": self._api_key,
            "file_type": "json",
            "observation_start": start.isoformat(),
            "observation_end": end.isoformat(),
        }

        retrieved_at = datetime.now(UTC)
        try:
            if self._http_client is not None:
                response = await self._http_client.get(
                    self.endpoint, params=params, timeout=self._timeout
                )
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(self.endpoint, params=params)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict) or not isinstance(payload.get("observations"), list):
                raise DataProviderError("FRED returned an unexpected response format.")
        except (httpx.HTTPError, ValueError) as exc:
            if isinstance(exc, DataProviderError):
                raise
            raise DataProviderError(f"FRED request failed: {exc}") from exc

        # Never expose the API key in a source URL or in an API response.
        source_url = f"https://fred.stlouisfed.org/series/{series_id}"
        observations: list[MacroObservation] = []
        try:
            for item in payload["observations"]:
                raw_value = str(item["value"]).strip()
                value = None if raw_value == "." else Decimal(raw_value)
                observations.append(
                    MacroObservation(
                        observation_date=date.fromisoformat(item["date"]),
                        value=value,
                        provider=self.provider_name,
                        series_id=series_id,
                        retrieved_at=retrieved_at,
                        source_url=source_url,
                    )
                )
        except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
            raise DataProviderError("FRED returned an invalid observation.") from exc

        return MacroSeriesResponse(
            provider=self.provider_name,
            series_id=series_id,
            observations=observations,
            retrieved_at=retrieved_at,
            source_url=source_url,
        )
