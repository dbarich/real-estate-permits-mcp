# ADR-001: Use MCP as the Primary Interface Protocol

**Status:** Accepted
**Date:** 2024-12-29 (retroactive — documented 2026-03-07)

## Context

The Real Estate Permits tool needed an interface that would allow natural-language interaction with structured municipal data. The options were: a traditional REST API, a CLI tool, a web application, or an MCP (Model Context Protocol) server.

The author was already using Claude Desktop for project management and wanted data queries integrated into the same conversational workflow used for document generation, analysis, and decision support.

## Decision

Build the tool as a FastMCP server that exposes data queries as tools callable by Claude Desktop and other MCP-compatible hosts.

## Alternatives Considered

| Alternative | Pros | Cons |
|------------|------|------|
| REST API | Broad compatibility, standard tooling | Requires separate client, no AI integration, more infrastructure |
| CLI tool | Simple, scriptable | No conversational interface, limited composability |
| Web application | Accessible to non-technical users | Heavy to build and maintain, hosting costs, authentication complexity |
| Jupyter notebook | Good for exploration | Not a product, not composable, poor UX for non-technical users |

## Consequences

**Positive:**
- Zero-infrastructure deployment (runs locally via Claude Desktop config)
- Natural language interface for free (Claude handles query interpretation)
- Composable with skills (market pull, document generation)
- Fast development cycle (FastMCP abstracts protocol details)

**Negative:**
- Limited to MCP-compatible hosts (currently Claude Desktop, potentially others)
- Excludes non-technical users who don't have Claude Desktop
- No web presence or discoverability
- Testing requires Claude Desktop or MCP client tooling

**Open Risk:**
- MCP is a young protocol. Adoption trajectory is promising (Anthropic backing, growing ecosystem) but not guaranteed.
- If the product needs to serve Persona 3 (Loan Officer), a REST API or web layer will be required regardless.

## Revisit Trigger

Revisit this decision if: (a) MCP adoption stalls, (b) a validated persona requires a non-MCP interface, or (c) a multi-city expansion makes local-only deployment impractical.
