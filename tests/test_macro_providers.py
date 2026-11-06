from datetime import date
from decimal import Decimal

import httpx
import pytest

from app.integrations.bcb import BCBProvider
from app.integrations.errors import DataProviderError
from app.integrations.fred import FREDProvider


@pytest.mark.asyncio
async def test_bcb_provider_normalizes_brazilian_decimal_and_date() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["dataInicial"] == "01/01/2025"
        return httpx.Response(
            200,
            json=[{"data": "02/01/2025", "valor": "6,25"}],
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await BCBProvider(http_client=client).get_series(
            "11", date(2025, 1, 1), date(2025, 1, 31)
        )

    assert result.provider == "bcb"
    assert result.series_id == "11"
    assert result.observations[0].observation_date == date(2025, 1, 2)
    assert result.observations[0].value == Decimal("6.25")


@pytest.mark.asyncio
async def test_bcb_provider_rejects_non_numeric_series_code() -> None:
    with pytest.raises(ValueError, match="numeric"):
        await BCBProvider().get_series("SELIC")


@pytest.mark.asyncio
async def test_fred_provider_normalizes_observations_and_hides_api_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["api_key"] == "test-secret"
        return httpx.Response(
            200,
            json={
                "observations": [
                    {"date": "2025-01-01", "value": "4.25"},
                    {"date": "2025-02-01", "value": "."},
                ]
            },
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await FREDProvider(api_key="test-secret", http_client=client).get_series(
            "FEDFUNDS"
        )

    assert result.observations[0].value == Decimal("4.25")
    assert result.observations[1].value is None
    assert "test-secret" not in result.source_url


@pytest.mark.asyncio
async def test_fred_provider_requires_api_key() -> None:
    with pytest.raises(DataProviderError, match="FRED_API_KEY"):
        await FREDProvider(api_key="").get_series("FEDFUNDS")
