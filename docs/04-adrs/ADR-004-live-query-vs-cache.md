# ADR-004: Live API Queries vs. Cached Data

**Status:** Accepted (for Prototype); Revisit for Beta
**Date:** 2026-03-07

## Context

The MCP server currently queries Seattle Socrata and King County ArcGIS APIs in real-time for every tool call. This means every user request hits the external APIs directly.

## Decision

For the Prototype stage, continue with live queries. No caching layer.

## Alternatives Considered

| Alternative | Pros | Cons |
|------------|------|------|
| Live queries (current) | Always fresh data, no storage needed, simple | Slow (~2-5s per query), rate limit risk, API downtime = tool downtime |
| Local cache with TTL | Faster responses, resilient to API outages | Stale data risk, storage management, cache invalidation complexity |
| Nightly batch sync | Fastest queries, full local dataset | Heavy infrastructure, data staleness, storage costs, overkill for current scale |
| Hybrid (cache parcels, live permits) | Parcel data changes slowly, permits change daily | Added complexity, two data paths |

## Reasoning

At current usage (1 user, ~10-20 queries/week), live queries are fine. The APIs respond in 2-5 seconds, there's no rate limit pressure, and data freshness is maximized.

Caching becomes necessary when: (a) multiple users are querying simultaneously, (b) response time needs to be under 1 second, or (c) API reliability becomes an issue.

## Consequences

**Positive:**
- Simplest possible implementation
- Always-current data
- No infrastructure to maintain

**Negative:**
- 2-5 second latency per tool call (sometimes longer)
- No graceful degradation if APIs are down
- Can't do historical analysis (no stored data over time beyond manual snapshots)

## Revisit Trigger

Revisit for Beta, or earlier if: (a) response times exceed 10 seconds regularly, (b) rate limits are hit, or (c) the tool needs to support offline or historical queries.
