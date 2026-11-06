# External data providers

Provider selection is intentionally deferred until the first data integration milestone. The application uses provider interfaces so a vendor can be changed without changing the agent workflow.

## Initial geographic coverage

- **Brazil:** BCB SGS for selected macroeconomic and monetary series; B3 assets for market coverage through a provider whose licensing permits the intended use.
- **United States:** FRED for selected macroeconomic series; US-listed assets through the same market-data provider where coverage and licensing allow.
- **Display conventions:** BRL as the initial base/display currency, while preserving the original currency and unit returned by each source. Currency conversion must use a separately sourced FX observation and timestamp.

## Implemented macro adapters

- **BCB SGS:** `BCBProvider` calls the Banco Central do Brasil SGS time-series web service. It accepts a numeric SGS series code and converts the provider's Brazilian date and decimal formats into normalized Python values. If no date range is supplied, the adapter requests the most recent 365 days to avoid unbounded downloads.
- **FRED:** `FREDProvider` calls the FRED `series/observations` endpoint and requires `FRED_API_KEY`. The API key is read from environment-based settings and is never included in the public source URL returned by the application. If no date range is supplied, the adapter requests the most recent 365 days to keep responses bounded.
- Both adapters return the same `MacroSeriesResponse` / `MacroObservation` schema, preserving provider, series identifier, observation date, retrieval timestamp, value, and source URL. Values are represented as `Decimal`, not binary floating-point numbers.

Official documentation:
- BCB web services: https://www.bcb.gov.br/gestao_site/webservices.asp?frame=1
- BCB SGS open-data catalogue: https://dadosabertos.bcb.gov.br/
- FRED observations endpoint: https://fred.stlouisfed.org/docs/api/fred/series_observations.html

## Market research API requirements

- Quote and historical time-series endpoints
- Coverage for B3 and US-listed assets
- Symbol and exchange normalization
- Currency and unit metadata
- Rate limits, attribution, and commercial-use terms
- Explicit rules for delayed data, caching, display, and redistribution

## Macro API requirements

- Indicator series and observation dates
- Release/publication dates and revision metadata
- Units, frequency, seasonal adjustment, and geography
- Clear handling of delayed or revised observations
- Stable series identifiers and provider-specific metadata

## Candidate sources to evaluate

- FRED for selected US macroeconomic series
- BCB SGS for Brazilian macroeconomic series
- Official statistical and central-bank APIs for future geographies
- A market-data provider with suitable B3 and US coverage, licensing, and rate limits

No market-data provider is selected as a production dependency in this scaffold. Provider choice must consider not only API access and price, but also commercial use, attribution, display rights, caching, and redistribution restrictions.

Credentials must be stored in environment variables or a managed secret store, never committed.
