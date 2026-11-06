from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation

import httpx

from app.integrations.errors import DataProviderError
from app.integrations.schemas import MacroObservation, MacroSeriesResponse


class BCBProvider:
    """Adapter for Banco Central do Brasil's SGS time-series web service."""

    provider_name = "bcb"
    base_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"

    def __init__(
        self,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 10.0,
    ) -> None:
        self._http_client = http_client
        self._timeout = timeout

    async def get_series(
        self,
        series_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> MacroSeriesResponse:
        if not series_id.isdigit():
            raise ValueError("BCB SGS series_id must be a numeric series code.")

        today = datetime.now(UTC).date()
        end = end_date or today
        start = start_date or (end - timedelta(days=365))
        if start > end:
            raise ValueError("start_date must be on or before end_date.")

        url = f"{self.base_url}.{series_id}/dados"
        params = {
            "formato": "json",
            "dataInicial": start.strftime("%d/%m/%Y"),
            "dataFinal": end.strftime("%d/%m/%Y"),
        }
        retrieved_at = datetime.now(UTC)

        try:
            if self._http_client is not None:
                response = await self._http_client.get(url, params=params, timeout=self._timeout)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise DataProviderError("BCB returned an unexpected response format.")
        except (httpx.HTTPError, ValueError) as exc:
            if isinstance(exc, DataProviderError):
                raise
            raise DataProviderError(f"BCB SGS request failed: {exc}") from exc

        source_url = str(response.request.url)
        observations: list[MacroObservation] = []
        try:
            for item in payload:
                observation_date = datetime.strptime(item["data"], "%d/%m/%Y").date()
                raw_value = str(item["valor"]).strip()
                value = Decimal(raw_value.replace(".", "").replace(",", "."))
                observations.append(
                    MacroObservation(
                        observation_date=observation_date,
                        value=value,
                        provider=self.provider_name,
                        series_id=series_id,
                        retrieved_at=retrieved_at,
                        source_url=source_url,
                    )
                )
        except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
            raise DataProviderError("BCB returned an invalid observation.") from exc

        return MacroSeriesResponse(
            provider=self.provider_name,
            series_id=series_id,
            observations=observations,
            retrieved_at=retrieved_at,
            source_url=source_url,
        )
