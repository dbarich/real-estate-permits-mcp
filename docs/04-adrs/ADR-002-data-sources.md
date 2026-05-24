# ADR-002: Seattle Socrata + King County ArcGIS as Data Sources

**Status:** Accepted
**Date:** 2024-12-29 (retroactive — documented 2026-03-07)

## Context

The tool needs building permit data and property valuation data for Seattle. Multiple data sources exist at the city, county, and state level.

## Decision

Use two primary data sources:

1. **Seattle Open Data (Socrata API)** for building permits
   - Dataset `76t5-zqzr`: All building permits
   - Dataset `kkzf-ntnu`: Land use permits
   - Queried via SoQL (Socrata Query Language)

2. **King County ArcGIS PropertyInfo MapServer** for parcel and sales data
   - Layer 0: Parcel info (PIN, zoning, acreage, present use)
   - Layer 3: Property sales in last 3 years (address, sale price, buyer/seller)

## Alternatives Considered

| Alternative | Pros | Cons |
|------------|------|------|
| King County Assessor eReal Property (web scraping) | More detailed parcel data | Fragile, no API, TOS concerns |
| NWMLS data | Transaction-level detail | Requires paid access, licensing restrictions |
| Zillow API / Redfin data | Consumer valuations | Limited to estimates, no permit data, API restrictions |
| Washington State DOR | Statewide data | Less granular than county/city sources |

## Consequences

**Positive:**
- Both sources are free, public, and officially maintained
- No API keys required for basic access (Socrata has app tokens for higher rate limits)
- Data is authoritative (comes directly from the agencies that issue permits and assess property)
- Both support structured queries with filtering, sorting, and field selection

**Negative:**
- Two different APIs with different query languages (SoQL vs. ArcGIS REST)
- No guaranteed uptime or SLA (public APIs can be slow or temporarily unavailable)
- King County ArcGIS occasionally returns inconsistent field names or empty results
- Socrata rate limits without an app token (~1,000 requests/hour unauthenticated)
- Data freshness varies: permits may lag 1-5 days; sales data may lag weeks to months

**V2 Consideration:**
- For production use, consider adding a Socrata app token for higher rate limits
- Consider caching frequently-accessed parcel data locally to reduce API calls
- May need to add Washington State DOR data for tax and assessment history

## Revisit Trigger

Revisit if: (a) either API changes its access model, (b) multi-city expansion requires different data sources, or (c) data freshness becomes a validated user concern.
