# Product Narrative: Real Estate Permits MCP

## The Problem

Small-scale real estate developers — people building 2-8 unit projects on individual lots — make high-stakes financial decisions based on incomplete, fragmented, and manually gathered market data.

The data exists. Seattle's SDCI publishes every building permit through the Socrata open data API. King County's Assessor exposes parcel valuations, zoning, and sales history through ArcGIS. But accessing this data requires knowing which APIs exist, understanding their query languages, interpreting field names that vary across datasets, and stitching together permit activity with property valuations to form a coherent picture.

The result: developers either pay consultants thousands of dollars for market analysis, spend hours manually searching county websites, or — most commonly — make decisions on gut feel and incomplete comps. Banks see the same gap from the other side: loan applications arrive with thin market support, and underwriters lack confidence in the development context.

## The Origin

This product started as a personal tool. The author is developing a 4-level stacked dwelling unit project at 2412 S Dearborn St in Seattle's Judkins Park neighborhood. To support construction loan underwriting, he needed to repeatedly pull permit activity, parcel comparables, and market context for the surrounding corridor.

Rather than manually querying APIs each time, he built an MCP (Model Context Protocol) server that exposes Seattle permit and King County parcel data as tools that Claude can call directly. This turned hours of manual research into conversational queries: "What's the permit activity on Dearborn in the last year?" returns structured, current data in seconds.

On top of that, he built two Claude skills: an interactive research tool for ad-hoc queries and an automated bi-weekly market pull that generates formatted Word documents for bank submission.

**The tool works.** It has been used to produce real bank underwriting documents, track corridor development activity over time, and make a geotech contractor selection decision informed by comparable project data.

## The Question

The tool was built for one project. But the problem it solves is not unique to one project.

Every small-scale developer in Seattle faces the same data fragmentation. Every bank underwriter reviewing a construction loan in King County needs the same comparable context. Every real estate agent evaluating a development site needs permit activity and parcel history in a usable form.

The question this product lifecycle is designed to answer: **Is this a product, and if so, for whom?**

## What This Product Is (Working Hypothesis)

An MCP server that gives AI assistants (and by extension, their users) structured access to municipal building permit and county property data — starting with Seattle/King County. It turns public municipal data into conversational intelligence for real estate decision-making.

## What This Product Is NOT

- Not a full MLS replacement or real estate listing service
- Not a construction project management tool
- Not a GIS/mapping platform
- Not a data warehouse (it queries live APIs, not stored data)
- Not currently multi-city (Seattle/King County only)

## Market Context

**Existing alternatives and why they're insufficient:**

| Alternative | What It Does | Gap |
|------------|-------------|-----|
| Seattle SDCI GIS Portal | Manual web search for permits | No API composability, no AI integration, no cross-reference with parcel data |
| King County Assessor website | Manual parcel lookup | One parcel at a time, no bulk comparison, no permit correlation |
| CoStar / Reonomy | Commercial real estate analytics | Expensive ($500+/mo), focused on large commercial, not small-scale residential |
| Redfin / Zillow | Consumer real estate data | No permit data, no development context, consumer-focused not developer-focused |
| Custom consultant reports | Tailored market analysis | $2,000-5,000 per report, stale on delivery, not repeatable |
| Raw Socrata/ArcGIS APIs | Direct data access | Requires technical skill, no pre-built queries, no AI integration |

**The gap:** Nobody is serving the small-scale developer (1-8 units) with structured, AI-accessible, repeatable municipal data intelligence at a price point that makes sense for sub-$1M projects.

## Differentiation Thesis

Three things make this different from querying the APIs directly:

1. **MCP protocol** — Data is exposed as tools that AI assistants can call conversationally. The user doesn't need to know SoQL or ArcGIS REST syntax. They ask questions in natural language and get structured answers.

2. **Pre-composed queries** — The tool combines permit data with parcel data, which come from entirely different systems (City of Seattle vs. King County). The `get_development_comparables` function does in one call what would otherwise require understanding two APIs, correlating results, and formatting output.

3. **Workflow integration** — Because it's MCP, it plugs into Claude Desktop (and potentially other MCP-compatible hosts) and can be composed with skills that generate documents, track changes over time, and produce bank-ready outputs.

## Open Questions

These are the questions the rest of the lifecycle artifacts should help answer:

1. **Who is the primary user?** The solo developer-investor? The real estate agent? The loan officer? The appraiser? Each implies different features, packaging, and pricing.

2. **Is Seattle the right starting point, or should the architecture be multi-city from day one?** Seattle has good open data, but the value proposition may depend on geographic coverage.

3. **Is MCP the right distribution channel, or should there also be a REST API / web interface?** MCP is powerful but requires a compatible AI host. A REST API would broaden access but lose the conversational integration.

4. **What's the data accuracy bar?** The current tool queries live APIs but does minimal validation. For professional use, data quality guarantees matter.

5. **What's the business model?** Open source with paid skills? SaaS with API metering? Free tool that drives consulting revenue? This decision shapes everything downstream.
