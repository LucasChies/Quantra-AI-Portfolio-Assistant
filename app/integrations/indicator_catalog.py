from typing import Literal

from pydantic import BaseModel, ConfigDict


class IndicatorDefinition(BaseModel):
    """Curated metadata for a supported macroeconomic indicator."""

    model_config = ConfigDict(frozen=True)

    key: str
    display_name: str
    country: str
    provider: Literal["bcb", "fred"]
    series_id: str
    unit: str
    frequency: str
    description: str
    seasonal_adjustment: str | None = None
    freshness_max_age_days: int
    source_url: str


# Initial catalogue deliberately includes only series whose provider IDs and
# metadata have been checked against the official source documentation.
_INDICATORS = (
    IndicatorDefinition(
        key="br.selic",
        display_name="Meta da taxa Selic",
        country="BR",
        provider="bcb",
        series_id="432",
        unit="% ao ano",
        frequency="daily",
        description="Meta para a taxa Selic definida pelo Copom.",
        freshness_max_age_days=5,
        source_url="https://dadosabertos.bcb.gov.br/dataset/432-taxa-de-juros---meta-selic-definida-pelo-copom",
    ),
    IndicatorDefinition(
        key="br.ipca",
        display_name="IPCA — variação mensal",
        country="BR",
        provider="bcb",
        series_id="433",
        unit="% ao mês",
        frequency="monthly",
        description="Variação mensal do Índice Nacional de Preços ao Consumidor Amplo.",
        freshness_max_age_days=50,
        source_url="https://www3.bcb.gov.br/sgspub/consultarvalores/consultarValoresSeries.do?method=consultarSeries&series=433",
    ),
    IndicatorDefinition(
        key="br.usd_brl",
        display_name="Dólar americano — venda",
        country="BR",
        provider="bcb",
        series_id="1",
        unit="BRL por USD",
        frequency="business_daily",
        description="Taxa de câmbio livre do dólar americano para venda.",
        freshness_max_age_days=5,
        source_url="https://dadosabertos.bcb.gov.br/dataset/1-taxa-de-cambio---livre---dolar-americano-venda---diario",
    ),
    IndicatorDefinition(
        key="us.fed_funds",
        display_name="Federal Funds Effective Rate",
        country="US",
        provider="fred",
        series_id="DFF",
        unit="percent",
        frequency="daily",
        description="Effective federal funds rate, not seasonally adjusted.",
        seasonal_adjustment="Not Seasonally Adjusted",
        freshness_max_age_days=5,
        source_url="https://fred.stlouisfed.org/series/DFF",
    ),
    IndicatorDefinition(
        key="us.cpi",
        display_name="Consumer Price Index — All Urban Consumers",
        country="US",
        provider="fred",
        series_id="CPIAUCSL",
        unit="index 1982-1984=100",
        frequency="monthly",
        description="CPI for all urban consumers, all items.",
        seasonal_adjustment="Seasonally Adjusted",
        freshness_max_age_days=50,
        source_url="https://fred.stlouisfed.org/series/CPIAUCSL",
    ),
    IndicatorDefinition(
        key="us.real_gdp",
        display_name="Real Gross Domestic Product",
        country="US",
        provider="fred",
        series_id="GDPC1",
        unit="billions of chained 2017 USD",
        frequency="quarterly",
        description="Real GDP, seasonally adjusted annual rate.",
        seasonal_adjustment="Seasonally Adjusted Annual Rate",
        freshness_max_age_days=120,
        source_url="https://fred.stlouisfed.org/series/GDPC1",
    ),
    IndicatorDefinition(
        key="us.unemployment",
        display_name="Unemployment Rate",
        country="US",
        provider="fred",
        series_id="UNRATE",
        unit="percent",
        frequency="monthly",
        description="U-3 unemployment rate, seasonally adjusted.",
        seasonal_adjustment="Seasonally Adjusted",
        freshness_max_age_days=50,
        source_url="https://fred.stlouisfed.org/series/UNRATE",
    ),
)

INDICATOR_CATALOG: dict[str, IndicatorDefinition] = {
    indicator.key: indicator for indicator in _INDICATORS
}


def list_indicators() -> list[IndicatorDefinition]:
    """Return the curated catalogue in a stable key order."""

    return [INDICATOR_CATALOG[key] for key in sorted(INDICATOR_CATALOG)]


def get_indicator(key: str) -> IndicatorDefinition | None:
    """Return one indicator definition, or None when the key is unknown."""

    return INDICATOR_CATALOG.get(key)
