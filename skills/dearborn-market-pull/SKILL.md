---
name: dearborn-market-pull
description: "Generate a dated market analysis report for the Bookstorhaus bank proposal. Pulls fresh permit and parcel data from Seattle SDCI and King County Assessor for the Judkins Park / Central District corridor, then produces a formatted Word document. Run this bi-weekly (every other Friday at 4pm) or on demand whenever fresh market data is needed for the underwriting package. Trigger when the user mentions market pull, bank report, underwriting update, bi-weekly report, or fresh comps."
---

# Dearborn Market Pull — Bi-Weekly Bank Proposal Report

Generate an updated market analysis document for the Bookstorhaus construction loan proposal at 2412 S Dearborn St, Seattle WA 98144.

## Objective

Pull current permit activity and property comparable sales data from the Judkins Park / Central District corridor, then produce a professionally formatted Word document suitable for bank underwriting review.

## Subject Property

- Address: 2412 S Dearborn St, Seattle WA 98144
- Parcel PIN: 6362900036
- Lot: 1,668 sq ft
- Zone: LR1(M)
- Acquisition: $249,000 (Feb 2023)
- Proposed: 4-level stacked dwelling units (daylight basement + 3 above-grade)
- SDCI confirmation: Stacked units approved, 36 ft height envelope (SMC 23.45.514.F)

## Prerequisite: Socrata app token (strongly recommended)

This skill fires 15+ data queries in a short burst. Seattle's Open Data API
throttles **unauthenticated** requests (shared per-IP pool), so a tokenless run
will usually get rate-limited (HTTP 429) and stall partway through.

Before running, check whether `SOCRATA_APP_TOKEN` is set in the MCP server's
environment. If it is **not** set, warn the user:

> Heads up — this report runs 15+ queries and Seattle throttles unauthenticated
> traffic, so it will likely stall without an app token. Get a free token at
> https://data.seattle.gov/profile/app_tokens, add it to your Claude Desktop MCP
> config under `env` as `SOCRATA_APP_TOKEN`, and restart Claude Desktop.

This is a soft warning, not a hard stop: if the user wants to proceed anyway,
continue — single broad queries may still succeed, and any 429 will now return
an actionable message explaining the token fix.

## Steps

### Step 1: Pull Permit Data

Run these MCP tool calls to gather current permit activity:

1. Use `get_development_comparables` for address "2412 S Dearborn St" with days_back=365
2. Use `search_permits` for street names: DEARBORN, JUDKINS, RAINIER, JACKSON, MASSACHUSETTS, PLUM (days_back=365 each)
3. Use `get_multifamily_permits` with days_back=365, limit=50

Focus on permits with construction values above $100K, as these are most likely to represent new construction or significant multi-unit projects.

### Step 2: Pull Parcel Comparables

Run these MCP tool calls for property sales data:

1. Use `get_parcel_by_address` for the subject property: "2412 S Dearborn St"
2. Use `get_nearby_parcels` for address "2412 S Dearborn St"
3. Use `get_parcel_by_address` for key comps: "2510 S Dearborn St", "2509 S Dearborn St", "1902 S Dearborn St", "1712 S Dearborn St"
4. Look up any new high-value permit addresses from Step 1 using `get_parcel_by_address`

### Step 3: Diff Against Previous Snapshot

Before generating the report, check for previous snapshots in the Bookstorhaus workspace:

```
~/Bookstorhaus/market_snapshots/*.json
```

If a previous snapshot exists, load the most recent one and compare against the current pull. Identify:

1. **New permits** — permits that appear in the current pull but not in the previous snapshot (match by address + value + date)
2. **Status changes** — permits whose status changed (e.g., "Issued" to "Completed")
3. **New parcel sales** — parcels with a more recent sale date than the previous snapshot recorded
4. **Price movements** — parcels that appear in both snapshots but with a different sale price (indicates a new transaction)
5. **Dropped permits** — permits that appeared in the previous snapshot but no longer appear (may have expired or been revoked)

Save the current data as a new snapshot:
```
~/Bookstorhaus/market_snapshots/YYYY-MM-DD.json
```

Use the same JSON schema as the baseline snapshot (see existing files in that directory for the format). This creates a growing timeline of market data that the bank can review.

### Step 4: Generate the Word Document

Read the docx skill at `/sessions/elegant-amazing-wozniak/mnt/.skills/skills/docx/SKILL.md` for formatting guidance.

Create a Word document using docx-js (npm docx package) with these sections:

1. **Title Page** — "Development Market Analysis", Judkins Park / Central District Corridor, dated, subject property details
2. **Executive Summary** — 2-3 paragraphs summarizing findings and SDCI confirmation
3. **Changes Since Last Report** (skip for the first report) — A section highlighting what changed since the previous pull. Include:
   - New permits issued (table with address, value, date)
   - Permit status changes (address, old status, new status)
   - New parcel sales or price movements (address, old price, new price, date)
   - Any dropped/expired permits
   - A brief narrative interpreting the changes (e.g., "Two new permits in the immediate corridor suggest accelerating development activity")
   - If nothing changed, state "No material changes since [previous date]" — this is also useful for the bank as it shows monitoring consistency
4. **Dearborn Corridor Permit Activity** — Table of permits on S Dearborn St with address, value, status, date, notes
5. **Broader Area Development Activity** — Table of significant permits ($100K+) on surrounding streets
6. **Property Comparable Sales** — Table with address, PIN, lot size, sale price, date, notes. Subject property bolded.
7. **Key Comparable Observations** — Bullet points highlighting the most bank-relevant comps
8. **Market Signal Summary** — Narrative connecting permit activity and parcel values to loan viability
9. **Report Timeline** — List of all previous report dates with a one-line summary of key changes from each (builds a running log the bank can scan). Format: "Feb 26, 2026 (Baseline) — Initial market pull. 14 permits tracked, 6 parcel comps established."
10. **Data Currency** — Report date, data sources, note about bi-weekly regeneration

Formatting requirements:
- US Letter size (12240 x 15840 DXA)
- Arial font throughout
- Navy blue headers (#1B3A5C)
- Professional table styling with alternating row shading
- Header: "Bookstorhaus Development | Market Analysis" with date
- Footer: "Confidential | Prepared for US Bank Underwriting Review" with page numbers

Save the file to the Bookstorhaus workspace with a dated filename:
`~/Bookstorhaus/Bookstorhaus_Market_Analysis_YYYY-MM-DD.docx`

Validate the document using:
```bash
python scripts/office/validate.py <output-path>
```

### Step 5: Summary

After generating the document, provide a brief summary to the user highlighting: how many new permits appeared, any notable sales or price movements, and whether the overall market signal is strengthening, stable, or weakening relative to the loan application narrative.

## Schedule

Intended to run bi-weekly, every other Friday at 4pm Pacific.
Cron expression (for future automation): `0 16 */14 * 5`

## Success Criteria

- Word document created and validated without errors
- All MCP data sources queried successfully
- Document contains current permit and parcel data
- File saved to workspace with dated filename
