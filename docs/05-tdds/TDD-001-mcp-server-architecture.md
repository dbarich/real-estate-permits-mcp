# TDD-001: MCP Server Architecture

**Status:** Current (documents existing implementation)
**Date:** 2026-03-07
**Relates to:** ADR-001, ADR-002, ADR-004

## Overview

The Real Estate Permits MCP server is a single-file Python application (currently implementing Seattle/King County data sources) that exposes 8 tools via the Model Context Protocol. It queries two external APIs (Seattle Socrata, King County ArcGIS) and returns formatted text summaries.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Desktop                          │
│                                                             │
│   User ──▶ Natural Language ──▶ Tool Selection ──▶ Tool Call│
└──────────────────────────┬──────────────────────────────────┘
                           │ MCP Protocol (stdio)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              seattle_permits_server.py                       │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────────────────────┐│
│  │  FastMCP Server   │  │         Tool Definitions         ││
│  │  (protocol layer) │  │                                  ││
│  │                   │  │  search_permits()                ││
│  │  - Tool registry  │  │  search_permits_by_zip()         ││
│  │  - I/O handling   │  │  get_multifamily_permits()       ││
│  │  - Error wrapping  │  │  get_permit_details()            ││
│  └──────────────────┘  │  get_parcel_by_address()          ││
│                         │  get_parcel_by_pin()              ││
│                         │  get_nearby_parcels()             ││
│                         │  get_development_comparables()    ││
│                         └──────────────────────────────────┘│
│                                                             │
│  ┌──────────────────┐  ┌──────────────────────────────────┐│
│  │  query_socrata()  │  │     query_kc_layer()             ││
│  │  (Seattle API)    │  │     (King County API)            ││
│  └────────┬─────────┘  └────────────┬─────────────────────┘│
└───────────┼─────────────────────────┼───────────────────────┘
            │ HTTPS                   │ HTTPS
            ▼                         ▼
┌──────────────────────┐  ┌──────────────────────────────────┐
│  data.seattle.gov    │  │  gismaps.kingcounty.gov          │
│  (Socrata API)       │  │  (ArcGIS MapServer)              │
│                      │  │                                  │
│  Building Permits    │  │  Layer 0: Parcels                │
│  Land Use Permits    │  │  Layer 3: Sales                  │
└──────────────────────┘  └──────────────────────────────────┘
```

## Tool Inventory

| Tool | Input | External API | Output |
|------|-------|-------------|--------|
| `search_permits` | street_name, days_back | Socrata (building_permits) | Permit list with address, type, status, cost, date |
| `search_permits_by_zip` | zip_code, permit_type, days_back | Socrata (building_permits) | Permit list filtered by ZIP |
| `get_multifamily_permits` | days_back, limit | Socrata (building_permits) | Multi-unit permits with descriptions |
| `get_permit_details` | permit_number | Socrata (building_permits) | Single permit full detail |
| `get_parcel_by_address` | address | KC ArcGIS Layer 3 | Parcel PIN, sale price, lot area, property type |
| `get_parcel_by_pin` | pin | KC ArcGIS Layers 0+3 | Zoning, use code, sale price, buyer/seller |
| `get_nearby_parcels` | address, property_type | KC ArcGIS Layer 3 | Sorted list of parcels on same street |
| `get_development_comparables` | address, days_back | Both (composite) | Combined permit activity + parcel sales |

## Data Flow

### Socrata Query Path
```
Input params ──▶ Build SoQL WHERE clause ──▶ HTTP GET to Socrata
                                                    │
                                              JSON response
                                                    │
                                              Format as text lines
                                                    │
                                              Return string to MCP
```

### King County Query Path
```
Input params ──▶ Build ArcGIS WHERE clause ──▶ HTTP GET to MapServer
                                                    │
                                              JSON response with features[]
                                                    │
                                              Extract attributes from features
                                                    │
                                              Format as text lines
                                                    │
                                              Return string to MCP
```

## Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| `mcp` | (FastMCP) | MCP protocol server framework |
| `httpx` | any | Async HTTP client for API calls |
| Python | 3.10+ | Runtime |

## Known Limitations

1. **No input validation:** Street names and addresses are passed directly into query strings without sanitization. SQL injection is not a risk (Socrata/ArcGIS APIs handle this) but garbage input produces garbage results.

2. **Address parsing is naive:** `get_nearby_parcels` and `get_development_comparables` extract street names by skipping directional prefixes and suffixes. This fails for streets like "Martin Luther King Jr Way" or numbered streets like "23rd Ave".

3. **No pagination:** Socrata queries are limited to 100 results. If more exist, they're silently truncated. King County queries return all matching features with no limit.

4. **Text-only output:** All tools return formatted strings. There's no structured data output (JSON mode) that downstream tools could parse programmatically.

5. **No error differentiation:** API timeouts, no-results, and server errors all produce similar error strings. The calling AI can't distinguish "no data exists" from "the API is down."

6. **Hardcoded datasets:** Socrata dataset IDs are hardcoded. If Seattle changes dataset IDs (rare but possible), the server breaks silently.

7. **No rate limiting:** No request throttling. If a skill triggers many parallel tool calls, all hit the external APIs simultaneously.

8. **Timestamp handling:** King County returns timestamps in milliseconds since epoch. The conversion assumes local timezone, which could produce wrong dates in UTC contexts.

## Improvement Candidates (for future TDDs)

| Improvement | Impact | Effort | Priority |
|------------|--------|--------|----------|
| Input validation and normalization | Reliability | Low | High |
| Structured JSON output mode | Composability | Medium | High |
| Error type differentiation | Debuggability | Low | Medium |
| Address parsing library (usaddress) | Accuracy | Low | Medium |
| Socrata app token for rate limits | Scalability | Low | Medium |
| Result pagination | Completeness | Medium | Low |
| Response caching (TTL-based) | Performance | Medium | Low (for now) |
| Land use permit integration | Feature | Medium | Low |
