from typing import Protocol


class MacroDataProvider(Protocol):
    """Contract for external macroeconomic-data providers."""

    async def get_indicator(self, indicator: str, **params: object) -> dict[str, object]:
        """Return a normalized macro observation or time series."""
        ...
