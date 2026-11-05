# Architecture

## Product scope

The initial product is B2C for individual investors. Brazil is the first market, Portuguese is the initial language, and BRL is the primary display currency. The product will cover B3 assets and international investments, starting with the US market.

The architecture should support future localization and multiple markets without coupling the application to one country's data conventions.

## Independence boundary

This application is fully standalone. It has no runtime dependency on Quantra V2 and does not share its database, identity system, or internal modules. Market and macro research is obtained through external provider APIs behind adapter interfaces.

## Data responsibilities

- **RAG / pgvector:** reports, research notes, methodology documents, and other unstructured sources.
- **External APIs:** current quotes, historical market series, macroeconomic indicators, and publication metadata.
- **LangGraph:** routes requests to retrieval and research tools, synthesizes evidence, and checks that responses are supported.
- **FastAPI:** exposes the service boundary.
- **Portfolio data:** initially imported by the user (for example, CSV) or represented by synthetic demo fixtures. No personal portfolio data is sourced from Quantra V2.

## Trust and freshness

Every external observation should preserve provider, source URL where available, retrieval timestamp, observation date, units, currency, and relevant frequency metadata. The answer layer must not present missing, stale, or unavailable values as current facts.

Market prices and macroeconomic observations must remain distinct concepts: a quote timestamp is not interchangeable with an economic observation date or a release date.

## Initial workflow

1. Classify the user question.
2. Retrieve relevant documents when background knowledge is required.
3. Call market and/or macro APIs when structured facts are required.
4. Synthesize an answer with source references and timestamps.
5. Validate evidence and disclose gaps.

Portfolio-specific data connections are intentionally out of scope for the standalone MVP. Future SaaS capabilities should introduce tenant isolation, user-controlled data retention, usage limits, and auditability before onboarding real customer portfolios.
