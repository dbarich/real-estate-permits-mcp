# Quick Start Guide

This tool connects Claude Desktop to Seattle's public building permit and property databases. Instead of clicking through government portals, you ask questions in plain English and get structured results.

## Setup (5 minutes)

**Prerequisites:** Python 3.8+, [Claude Desktop](https://claude.ai/download)

```bash
git clone https://github.com/dbarich/real-estate-permits-mcp.git
cd real-estate-permits-mcp
chmod +x setup.sh && ./setup.sh
```

The script installs dependencies, verifies the APIs are reachable, and configures Claude Desktop. Restart Claude Desktop when prompted.

**Verify it works:** Open Claude Desktop and type: *"Search for building permits on Dearborn Street in the last 6 months."* You should see structured permit results with addresses, types, costs, and dates.

## What You Can Do

The tool exposes 8 capabilities to Claude. You don't need to know the tool names — just ask questions naturally. Here are some starting points:

### Permit Research
- "What building permits have been issued near Rainier Ave in the last year?"
- "Show me multifamily or townhouse permits citywide from the last 2 years"
- "Look up permit number 6808042-CN"
- "Find all permits in ZIP 98144 for new construction"

### Property Lookup
- "What's the zoning and lot size for 2412 S Dearborn St?"
- "Look up parcel 6362900036 — give me zoning, assessed value, and last sale"
- "Find all properties on S Jackson St and sort by appraised value"

### Development Comparables
- "Pull development comparables for 2412 S Dearborn St — I need recent permits and nearby property values for a loan application"

### Multi-Step Analysis
Claude can chain these together. Try:
- "I'm considering developing a property at [address]. What's the zoning, what permits have been issued nearby, and what are the comparable property values?"
- "Compare permit activity on Dearborn St vs Jackson St over the last 2 years"

## What the Data Actually Is

**Building permits** come from Seattle's open data portal (data.seattle.gov). Coverage includes all permits filed with SDCI — new construction, additions, alterations, demolitions. Fields include address, permit type, status, estimated project cost, issued date, contractor.

**Property/parcel data** comes from King County's Assessor GIS (gismaps.kingcounty.gov). Coverage includes every parcel in King County — zoning, lot size, appraised land and improvement values, present use classification. Sales data covers the most recent ~3 years.

Neither source requires an API key. Both are free, public, and updated regularly by the respective government agencies.

## Known Limitations

- **Seattle only.** Permit data is Seattle SDCI permits. Parcel data covers King County but the tool is optimized for Seattle addresses.
- **Address matching is imperfect.** The tool tries multiple address format variants (directionals, suffixes) but some addresses may not match on the first try. If an address lookup fails, try the PIN instead.
- **Sales data is ~3 years.** King County's sales layer only includes recent transactions. Properties that haven't sold recently will show "no sale in past ~3 years."
- **No caching.** Every query hits the live API. During heavy use, you may occasionally see rate limiting (add a Socrata app token to avoid this — see README).

## Evaluation Questions

If you're testing this tool, here are the questions we'd love your input on:

1. **Would you use this?** If you were evaluating a small development site in Seattle, does this save you meaningful time vs. manually searching data.seattle.gov and the King County parcel viewer?

2. **Is the Claude interface enough?** Or would you want a dashboard, a web form, or a different way to interact with this data?

3. **What's missing?** What data would make this more useful? Zoning interpretation? Historical trends? Inspection status? Sales price per square foot?

4. **Who else would use this?** Beyond developers — would a real estate agent, a lender, or a city planner find this valuable?

5. **Data quality.** Does anything look wrong, incomplete, or misleading in the results you see?

File issues or feedback at: https://github.com/dbarich/real-estate-permits-mcp/issues
