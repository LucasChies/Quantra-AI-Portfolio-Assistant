# Quantra AI Portfolio Assistant

An independent AI-powered portfolio research assistant for individual investors (B2C), starting in Brazil and covering both Brazilian and international investments.

> This project is fully independent from Quantra V2. It does not depend on Quantra V2 services, database, authentication, or internal APIs. External data providers are accessed through replaceable provider adapters.

## Product direction

- **Audience:** individual investors, from beginners to experienced self-directed investors.
- **Initial market:** Brazil, with Portuguese as the first product language and BRL as the primary display currency.
- **Investment coverage:** Brazilian assets (starting with B3) and international assets (starting with the US market).
- **Future business model:** a SaaS product with free and paid subscription tiers.
- **Product principle:** explain portfolio exposures, market context, risks, and scenarios with traceable evidence. Do not present unsupported buy/sell instructions as certainty.

## Project goals

- Answer investment and portfolio-research questions with traceable evidence.
- Use RAG for research documents, reports, and explanatory material.
- Use external APIs for structured market and macroeconomic data (prices, indicators, releases, and time series).
- Orchestrate retrieval, API research, synthesis, and evidence checks with LangGraph.
- Keep provider integrations replaceable and secrets out of source control.
- Demonstrate production-minded engineering: tests, CI, containerization, observability, and infrastructure as code.

## Architecture principles

1. **RAG is for unstructured knowledge.** Documents are chunked, embedded, stored in pgvector, and retrieved with metadata and source references.
2. **APIs are for current structured facts.** Market and macro values are fetched from external providers through explicit adapters; they are not guessed from embeddings.
3. **Evidence before answers.** Responses should distinguish sourced facts from interpretation and say when evidence is insufficient or stale.
4. **Provider independence.** API providers, embedding models, and LLM deployments are configured behind interfaces.
5. **Privacy by design.** Public demos and tests use synthetic portfolios and sample documents only.
6. **Commercial readiness without premature complexity.** Keep user data ownership, tenant isolation, data licensing, and usage-cost controls in the architecture; implement SaaS billing and advanced tenancy in a later phase.

## Initial technology direction

- Python 3.12+
- FastAPI
- LangGraph / LangChain
- Azure OpenAI (LLM and embeddings; configurable)
- PostgreSQL + pgvector
- External market and macro data APIs (provider selection via configuration)
- Docker-compatible containers / Podman
- GitHub Actions
- Terraform and Azure Container Apps (deployment phase)

## Planned request flow

```text
User question
    |
FastAPI
    |
LangGraph workflow
    +--> classify intent
    +--> retrieve documents (RAG / pgvector)
    +--> fetch market or macro data (external API adapters)
    +--> synthesize answer with citations
    +--> validate evidence, freshness, and limitations
    |
Grounded response
```

## Repository layout

The initial scaffold is being established. The application will be organized into API routes, agent graph and nodes, RAG ingestion/retrieval, external data-provider adapters, tests, documentation, and deployment infrastructure.

## Local development

Setup instructions will be added with the first runnable vertical slice. Never commit real API keys, credentials, personal portfolio data, or production exports. Copy `.env.example` to `.env` and use synthetic fixtures for local development.

## Roadmap

- [x] Repository scaffold and engineering conventions
- [x] FastAPI health endpoint and configuration
- [ ] Define normalized macro and market data contracts
- [ ] Implement Brazilian macro data adapter (BCB SGS)
- [ ] Implement US macro data adapter (FRED)
- [ ] Select a market-data provider after coverage and commercial-license review
- [ ] LangGraph workflow with deterministic test doubles
- [ ] RAG ingestion and pgvector retrieval
- [ ] Evidence citations, freshness checks, and fallback behavior
- [ ] Automated tests and GitHub Actions
- [ ] Container build and local development environment
- [ ] Portfolio import and analysis using synthetic/demo data first
- [ ] Independent frontend inspired by the Quantra visual language
- [ ] Terraform and Azure deployment
- [ ] SaaS foundations: authentication, tenant isolation, usage controls, and billing

## Disclaimer

This software is an educational and engineering portfolio project. It is not investment advice, does not guarantee data accuracy or availability, and must not be used as the sole basis for financial decisions.
