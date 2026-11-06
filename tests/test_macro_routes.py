from datetime import UTC, date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.macro import get_bcb_provider, get_fred_provider
from app.integrations.fred import FREDProvider
from app.integrations.schemas import MacroObservation, MacroSeriesResponse


client = TestClient(app)


class FakeBCBProvider:
    async def get_series(
        self,
        series_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> MacroSeriesResponse:
        retrieved_at = datetime.now(UTC)
        source_url = "https://api.bcb.gov.br/example"
        observation = MacroObservation(
            observation_date=date(2025, 1, 2),
            value=Decimal("6.25"),
            provider="bcb",
            series_id=series_id,
            retrieved_at=retrieved_at,
            source_url=source_url,
        )
        return MacroSeriesResponse(
            provider="bcb",
            series_id=series_id,
            observations=[observation],
            retrieved_at=retrieved_at,
            source_url=source_url,
        )


def test_bcb_macro_route_returns_normalized_observation() -> None:
    app.dependency_overrides[get_bcb_provider] = FakeBCBProvider
    try:
        response = client.get("/api/v1/macro/bcb/11")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "bcb"
    assert payload["series_id"] == "11"
    assert payload["observations"][0]["value"] == "6.25"


def test_fred_macro_route_maps_missing_credentials_to_bad_gateway() -> None:
    app.dependency_overrides[get_fred_provider] = lambda: FREDProvider(api_key="")
    try:
        response = client.get("/api/v1/macro/fred/FEDFUNDS")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json()["detail"] == "FRED_API_KEY is not configured."
