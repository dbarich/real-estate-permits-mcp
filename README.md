# Real Estate Permits MCP

> An MCP server that gives Claude access to Seattle building permits and King County property data. Ask questions in plain English, get structured answers from public records.

**Status: alpha** — Working prototype, single-user validated. Built for a real construction loan application. Looking for early feedback from developers and real estate professionals in the Seattle market.

## What it does

This server connects Claude Desktop to two public data APIs — Seattle Open Data (building permits) and King County ArcGIS (parcel and sales records). Instead of clicking through government portals, you ask questions:

```
"What permits have been issued on Dearborn St in the last year?"
"What's the zoning and assessed value for this parcel?"
"Show me development comparables near my site."
```

The server figures out which APIs to query, pulls the data, and returns structured results. A research task that used to take 2-3 hours now takes 5 minutes.

## Who it's for

Small-scale real estate developers building 2-8 unit projects who need market context for loan applications, feasibility studies, and investor pitches. The tool was built by one — and validated against a real bank underwriting process.

There's also a hypothesis (unvalidated) that lenders could use the same tool to independently verify market claims in construction loan applications. If you're on that side of the table, we'd especially like to hear from you.

## Quick start

### Prerequisites

- Python 3.10+
- Claude Desktop (or any MCP-compatible host)

### Install

```bash
git clone https://github.com/devinbarich/real-estate-permits-mcp.git
cd real-estate-permits-mcp
pip install mcp httpx
```

### Configure Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "real-estate-permits": {
      "command": "python",
      "args": ["/path/to/real-estate-permits-mcp/src/seattle_permits_server.py"]
    }
  }
}
```

Restart Claude Desktop. The 8 tools will appear in your tool list.

No API keys required — both data sources are free and public.

## Available tools

| Tool | What it does |
|------|-------------|
| `search_permits` | Search building permits by street name |
| `search_permits_by_zip` | Search permits by ZIP code with optional type filter |
| `get_multifamily_permits` | Find multi-unit building permits citywide |
| `get_permit_details` | Look up a specific permit by number |
| `get_parcel_by_address` | Get King County parcel info (zoning, lot size, assessed value) |
| `get_parcel_by_pin` | Get parcel info by Parcel ID Number |
| `get_nearby_parcels` | Find comparable parcels near an address |
| `get_development_comparables` | Combined permit + parcel analysis for a target address |

## Example skills

The `skills/` directory includes two Claude skills that demonstrate how to build workflows on top of the MCP server:

- **dearborn-mcp** — Interactive research skill for ad-hoc corridor queries (ZIP codes 98144/98122)
- **dearborn-market-pull** — Automated bi-weekly market report that generates formatted Word documents for bank submission

These are real skills used in production for a Judkins Park construction project. Fork and adapt them for your own target area.

## Data sources

- **Seattle Open Data** (Socrata API): [data.seattle.gov](https://data.seattle.gov) — Building permits, land use permits
- **King County ArcGIS**: PropertyInfo MapServer — Parcel data, assessed values, property sales

Both are free, public, and require no API key for basic access. An optional Socrata app token (set via environment variable) increases rate limits.

## Documentation

The `docs/` directory contains a full product lifecycle framework — not just technical docs, but the thinking behind what this is and where it's going:

- [Product Lifecycle](docs/00-product-lifecycle/LIFECYCLE.md) — 8-stage framework and current status
- [Narrative](docs/01-narrative/NARRATIVE.md) — Why this exists, market thesis
- [Use Cases](docs/02-use-cases/USE_CASES.md) — What people do with it (3 proven, 4 projected)
- [Personas](docs/03-personas/PERSONAS.md) — Who the users are
- [Architecture Decisions](docs/04-adrs/) — ADR-001 through ADR-004
- [Technical Design](docs/05-tdds/) — Server architecture and API contracts
- [Roadmap](docs/06-roadmap/ROADMAP.md) — Hardening, Beta, V1, Expansion
- [Metrics](docs/07-metrics/METRICS.md) — How we measure success

## Known limitations

This is an alpha. Things that don't work yet:

- **No input validation** — bad addresses fail silently or return empty results
- **No error differentiation** — API timeouts and "no results" look the same
- **Seattle only** — the data sources are Seattle/King County specific
- **No tests** — the test suite is empty (first priority for hardening)
- **No caching** — every query hits the live API

See the [Roadmap](docs/06-roadmap/ROADMAP.md) for the hardening plan.

## Contributing

This project is in early alpha. The most valuable thing you can do right now is:

1. **Try to install it** and tell us if the instructions work
2. **Use it for a real task** and tell us what broke or was confusing
3. **Open an issue** with your experience — good or bad

If you're in a different city and interested in building a data adapter, see [ADR-003](docs/04-adrs/ADR-003-single-city-start.md) for the single-city rationale and what a multi-city architecture might look like.

## License

MIT — see [LICENSE](LICENSE).
