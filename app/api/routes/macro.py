from datetime import UTC, date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.integrations.bcb import BCBProvider
from app.integrations.errors import DataProviderError
from app.integrations.fred import FREDProvider
from app.integrations.freshness import assess_freshness
from app.integrations.indicator_catalog import get_indicator, list_indicators
from app.integrations.schemas import MacroSeriesResponse

router = APIRouter(prefix="/macro", tags=["macro"])


def get_bcb_provider() -> BCBProvider:
    return BCBProvider()


def get_fred_provider() -> FREDProvider:
    return FREDProvider()


@router.get("/bcb/{series_id}", response_model=MacroSeriesResponse)
async def get_bcb_series(
    series_id: str,
    provider: Annotated[BCBProvider, Depends(get_bcb_provider)],
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
) -> MacroSeriesResponse:
    try:
        return await provider.get_series(series_id, start_date, end_date)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DataProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/fred/{series_id}", response_model=MacroSeriesResponse)
async def get_fred_series(
    series_id: str,
    provider: Annotated[FREDProvider, Depends(get_fred_provider)],
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
) -> MacroSeriesResponse:
    try:
        return await provider.get_series(series_id, start_date, end_date)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DataProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/indicators")
async def get_indicator_catalog():
    """List the curated macroeconomic indicators supported by this API."""

    return list_indicators()


@router.get("/indicators/{key}", response_model=MacroSeriesResponse)
async def get_catalog_indicator_series(
    key: str,
    bcb_provider: Annotated[BCBProvider, Depends(get_bcb_provider)],
    fred_provider: Annotated[FREDProvider, Depends(get_fred_provider)],
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
) -> MacroSeriesResponse:
    indicator = get_indicator(key)
    if indicator is None:
        raise HTTPException(status_code=404, detail=f"Unknown macro indicator: {key}")

    provider = bcb_provider if indicator.provider == "bcb" else fred_provider
    try:
        result = await provider.get_series(indicator.series_id, start_date, end_date)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DataProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    observations = [
        observation.model_copy(update={"unit": indicator.unit})
        for observation in result.observations
    ]
    freshness = assess_freshness(
        observations=observations,
        frequency=indicator.frequency,
        max_age_days=indicator.freshness_max_age_days,
        evaluated_on=datetime.now(UTC).date(),
    )
    return result.model_copy(
        update={"observations": observations, "freshness": freshness}
    )
