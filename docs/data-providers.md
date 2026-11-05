# External data providers

Provider selection is intentionally deferred until the first data integration milestone. The application uses provider interfaces so a vendor can be changed without changing the agent workflow.

## Market research API requirements

- Quote and historical time-series endpoints
- Symbol and exchange normalization
- Currency and unit metadata
- Rate limits, attribution, and commercial-use terms

## Macro API requirements

- Indicator series and observation dates
- Release/publication dates and revision metadata
- Units, frequency, seasonal adjustment, and geography
- Clear handling of delayed or revised observations

## Candidate sources to evaluate

- FRED for selected US macroeconomic series
- BCB SGS for Brazilian macroeconomic series
- Official statistical and central-bank APIs for other geographies
- A market-data provider with suitable coverage, licensing, and rate limits

No provider is selected as a production dependency in this scaffold. Credentials must be stored in environment variables or a managed secret store, never committed.
