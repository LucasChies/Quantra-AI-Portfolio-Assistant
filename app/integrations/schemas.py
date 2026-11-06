from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MacroObservation(BaseModel):
    """One normalized observation returned by a macroeconomic data provider."""

    model_config = ConfigDict(frozen=True)

    observation_date: date
    value: Decimal | None
    unit: str | None = None
    provider: str
    series_id: str
    retrieved_at: datetime
    source_url: str


class MacroSeriesResponse(BaseModel):
    """A normalized time series plus the metadata needed to assess its provenance."""

    model_config = ConfigDict(frozen=True)

    provider: str
    series_id: str
    observations: list[MacroObservation] = Field(default_factory=list)
    retrieved_at: datetime
    source_url: str
