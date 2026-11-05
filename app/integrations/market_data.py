from typing import Protocol


class MarketDataProvider(Protocol):
    """Contract for external market-data providers."""

    async def get_quote(self, symbol: str) -> dict[str, object]:
        """Return a normalized quote with provider and timestamp metadata."""
        ...
