from datetime import date
from typing import Protocol

from app.integrations.schemas import MacroSeriesResponse


class MacroDataProvider(Protocol):
    """Common interface implemented by macroeconomic data providers."""

    async def get_series(
        self,
        series_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> MacroSeriesResponse:
        """Return normalized observations for a provider-specific series identifier."""
        ...
