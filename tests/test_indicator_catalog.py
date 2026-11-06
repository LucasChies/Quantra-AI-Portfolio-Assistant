from datetime import UTC, date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.api.routes.macro import get_bcb_provider, get_fred_provider
from app.integrations.schemas import MacroObservation, MacroSeriesResponse
from app.main import app


client = TestClient(app)


class FakeMacroProvider:
    provider_name = "bcb"

    async def get_series(
        self,
        series_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> MacroSeriesResponse:
        retrieved_at = datetime.now(UTC)
        source_url = "https://example.test/series"
        observation = MacroObservation(
            observation_date=date(2025, 1, 2),
            value=Decimal("6.25"),
            provider=self.provider_name,
            series_id=series_id,
            retrieved_at=retrieved_at,
            source_url=source_url,
        )
        return MacroSeriesResponse(
            provider=self.provider_name,
            series_id=series_id,
            observations=[observation],
            retrieved_at=retrieved_at,
            source_url=source_url,
        )


def test_indicator_catalog_lists_curated_indicators() -> None:
    response = client.get("/api/v1/macro/indicators")

    assert response.status_code == 200
    payload = response.json()
    keys = {item["key"] for item in payload}
    assert len(payload) == 7
    assert {"br.selic", "br.ipca", "br.usd_brl", "us.fed_funds", "us.cpi"} <= keys


def test_catalog_indicator_route_uses_provider_and_adds_unit() -> None:
    fake_provider = FakeMacroProvider()
    app.dependency_overrides[get_bcb_provider] = lambda: fake_provider
    try:
        response = client.get("/api/v1/macro/indicators/br.selic")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "bcb"
    assert payload["series_id"] == "432"
    assert payload["observations"][0]["unit"] == "% ao ano"


def test_catalog_indicator_route_returns_not_found_for_unknown_key() -> None:
    response = client.get("/api/v1/macro/indicators/br.unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown macro indicator: br.unknown"
