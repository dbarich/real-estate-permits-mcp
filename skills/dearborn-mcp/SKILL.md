---
name: dearborn-mcp
description: "Run Seattle permit and parcel research for the Judkins Park area. Use this skill whenever the user wants to pull permits, parcel data, development comps, or market context for the Judkins neighborhood (98144/98122). Also trigger when the user mentions Dearborn, stacked builds, multifamily comps, King County parcels, or bank proposal research — even casually."
---

# Dearborn MCP — Judkins Area Development Research

This skill runs the Seattle permits and parcel MCP tools to pull development context for the Judkins Park area. It targets new construction activity — particularly stacked flat and multifamily builds — across ZIP codes 98144 and 98122.

## What this skill does

When invoked, run the following research steps in order. Present results in a clear summary at the end.

### Step 1: Ask the user what they need

Present these options (the user can pick one or more):

1. **Area permit scan** — Pull recent new construction permits in 98144 and 98122
2. **Parcel comps** — Look up property values and lot details near a specific address
3. **Development comparables** — Combined permit + parcel analysis for a target address
4. **Permit detail lookup** — Get details on a specific permit number
5. **Full sweep** — Run everything (area scan + comps for a default or specified address)

If the user doesn't specify, default to "Full sweep" using 2412 S Dearborn St as the target address.

### Step 2: Execute the research

Based on the user's selection, run the appropriate MCP tools:

**For area permit scan:**
- Use `search_permits_by_zip` for ZIP 98144 with permit_type "New"
- Use `search_permits_by_zip` for ZIP 98122 with permit_type "New"
- Use `get_multifamily_permits` to find comparable stacked/multifamily projects citywide
- Run these in parallel when possible

**For parcel comps:**
- Ask the user for a target address (default: 2412 S Dearborn St)
- Use `get_parcel_by_address` for the target property
- Use `get_nearby_parcels` to find comparable lots

**For development comparables:**
- Ask the user for a target address (default: 2412 S Dearborn St)
- Use `get_development_comparables` for the combined analysis

**For permit detail lookup:**
- Ask the user for the permit number
- Use `get_permit_details` to pull the full record

**For full sweep:**
- Run all of the above using the target address

### Step 3: Summarize findings

Present the results organized by category:

1. **New Construction Activity** — How many new build permits in the area, what types, estimated values
2. **Parcel Context** — Target property details and comparable lot valuations
3. **Market Signal** — What the permit and parcel data suggest about development activity and property values in the Judkins corridor

Flag anything that would be relevant to a bank underwriting review — comparable project values, rental unit configurations, recent appraisals in the area.

### Step 4: Offer next steps

After presenting results, ask if the user wants to:
- Save the results as a formatted document (for the bank proposal)
- Dig deeper into any specific permit or parcel
- Adjust the search parameters (different ZIP, time range, permit type)
- Run a comparison against a different neighborhood
