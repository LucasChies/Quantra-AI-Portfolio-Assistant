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


## Curated macro indicator catalogue

The first catalogue is exposed through:

- `GET /api/v1/macro/indicators` — list supported indicator definitions.
- `GET /api/v1/macro/indicators/{key}` — retrieve observations using a stable application key.

Initial keys:

| Key | Source series | Frequency | Unit |
| --- | --- | --- | --- |
| `br.selic` | BCB SGS 432 | Daily | % p.a. |
| `br.ipca` | BCB SGS 433 | Monthly | % monthly |
| `br.usd_brl` | BCB SGS 1 | Business daily | BRL per USD |
| `us.fed_funds` | FRED DFF | Daily | Percent |
| `us.cpi` | FRED CPIAUCSL | Monthly | Index 1982-1984=100 |
| `us.real_gdp` | FRED GDPC1 | Quarterly | Billions of chained 2017 USD |
| `us.unemployment` | FRED UNRATE | Monthly | Percent |

Each definition records the provider series ID, country, unit, frequency, description, source URL, seasonal-adjustment metadata where applicable, and a per-indicator maximum age used by the freshness evaluator.

### Data freshness policy

The catalogue indicator endpoint now includes a `freshness` object with:

- `status`: `fresh`, `stale`, or `unknown`.
- `frequency`: the configured cadence (`daily`, `business_daily`, `monthly`, or `quarterly`).
- `observation_date`: the economic date represented by the latest observation.
- `age_days`: calendar days between `observation_date` and `evaluated_on`.
- `max_age_days`: the maximum permitted age configured for that indicator.
- `evaluated_on`: the UTC calendar date on which the assessment was performed.
- `reason`: a human-readable explanation of the classification.

The evaluator always measures age from `observation_date`, never from `retrieved_at`. Retrieval time describes when this application fetched the source; it does not make an old economic observation current.

The current catalogue policies are 5 calendar days for daily/business-daily series, 50 days for monthly series, and 120 days for quarterly series. These thresholds intentionally account for normal publication cadence and expected delays; monthly and quarterly observations are not judged by a generic 24-hour rule. The business-daily threshold also provides a small allowance for weekends and non-trading days. This version does not yet use an official holiday calendar or provider release calendar, so thresholds remain explicit, configurable policy rather than a claim that every release should have arrived by a particular date.

Classification rules:

- `fresh`: the latest observation has a numeric value, its date is not in the future, and its age is less than or equal to the configured maximum.
- `stale`: the latest observation has a numeric value but exceeds the configured maximum age.
- `unknown`: there are no observations, the latest value is missing, the observation date is in the future, or the frequency is unsupported.

The assessment uses an injected evaluation date in unit tests, making boundary cases deterministic and independent of the machine clock. The API supplies the current UTC date at request time.

Brazilian GDP and unemployment are intentionally not included in this first executable catalogue. They require an IBGE SIDRA adapter rather than pretending that the existing BCB SGS adapter can query them. An IBGE integration is a separate follow-up milestone.

The BCB series IDs and metadata are checked against the official BCB open-data catalogue; FRED series IDs and metadata are checked against the corresponding FRED series pages. See the links embedded in each catalogue entry.
