from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.integrations.bcb import BCBProvider
from app.integrations.errors import DataProviderError
from app.integrations.fred import FREDProvider
from app.integrations.schemas import MacroSeriesResponse

router = APIRouter(prefix="/macro", tags=["macro"])


def get_bcb_provider() -> BCBProvider:
    return BCBProvider()


def get_fred_provider() -> FREDProvider:
    return FREDProvider()


@router.get("/bcb/{series_id}", response_model=MacroSeriesResponse)
async def get_bcb_series(
    series_id: str,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    provider: Annotated[BCBProvider, Depends(get_bcb_provider)] = None,
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
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    provider: Annotated[FREDProvider, Depends(get_fred_provider)] = None,
) -> MacroSeriesResponse:
    try:
        return await provider.get_series(series_id, start_date, end_date)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DataProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
