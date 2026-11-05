# Architecture

## Independence boundary

This application is fully standalone. It has no runtime dependency on Quantra V2 and does not share its database, identity system, or internal modules. Market and macro research is obtained through external provider APIs behind adapter interfaces.

## Data responsibilities

- **RAG / pgvector:** reports, research notes, methodology documents, and other unstructured sources.
- **External APIs:** current quotes, historical market series, macroeconomic indicators, and publication metadata.
- **LangGraph:** routes requests to retrieval and research tools, synthesizes evidence, and checks that responses are supported.
- **FastAPI:** exposes the service boundary.

## Trust and freshness

Every external observation should preserve provider, source URL where available, retrieval timestamp, observation date, and units. The answer layer must not present missing, stale, or unavailable values as current facts.

## Initial workflow

1. Classify the user question.
2. Retrieve relevant documents when background knowledge is required.
3. Call market and/or macro APIs when structured facts are required.
4. Synthesize an answer with source references and timestamps.
5. Validate evidence and disclose gaps.

Portfolio-specific data connections are intentionally out of scope for the standalone MVP.
