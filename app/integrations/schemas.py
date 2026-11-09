from datetime import date, datetime
from decimal import Decimal
from typing import Literal

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


class FreshnessMetadata(BaseModel):
    """Freshness assessment for the latest available economic observation."""

    model_config = ConfigDict(frozen=True)

    status: Literal["fresh", "stale", "unknown"]
    frequency: str
    observation_date: date | None
    age_days: int | None
    max_age_days: int
    evaluated_on: date
    reason: str


class MacroSeriesResponse(BaseModel):
    """A normalized time series plus provenance and optional quality metadata."""

    model_config = ConfigDict(frozen=True)

    provider: str
    series_id: str
    observations: list[MacroObservation] = Field(default_factory=list)
    retrieved_at: datetime
    source_url: str
    freshness: FreshnessMetadata | None = None
