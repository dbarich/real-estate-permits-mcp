# Personas: Real Estate Permits MCP

## How to Read This Document

Each persona includes a "Discovery Status" — whether this persona is grounded in real usage or hypothesized. The product should be built for validated personas first and validated against hypothesized personas before investing in features specific to them.

---

## Persona 1: The Solo Developer-Investor

**Discovery Status:** Validated (this is the author; usage is proven)

**Name:** Devin — the builder-operator

**Profile:**
- Individual developing 1-8 unit residential projects in Seattle
- Handles site selection, financing, permitting, and contractor management personally
- Technical enough to configure MCP servers and write Python scripts
- Not a full-time developer — wears many hats (finance, construction, marketing)
- Working on projects in the $500K-$2M total development cost range
- Relationship with a specific bank; needs to repeatedly demonstrate market context

**Goals:**
- Make data-backed decisions about site feasibility, contractor selection, and financing
- Produce professional-quality market analysis for bank underwriting without hiring a consultant
- Track corridor development activity over months to spot trends and adjust project timing
- Minimize time spent on manual data gathering so more time goes to actual development work

**Pain Points:**
- Public data exists but is fragmented across multiple agencies with different APIs and interfaces
- Manual research takes 2-4 hours per pull; needs to be repeated regularly
- Consultant reports cost $2,000-$5,000, are stale on delivery, and can't be updated incrementally
- Bank underwriters ask for "comparables" but don't specify exactly what data they need — the developer has to guess what will be convincing

**Technical Profile:**
- Comfortable with: Claude Desktop, MCP configuration, basic Python, command line
- Familiar with: APIs, JSON, CSV data formats
- Not interested in: Building web UIs, managing servers, DevOps

**Relationship to Product:**
- Power user who configures and customizes
- Builds skills on top of the MCP server for specific workflows
- Values flexibility and composability over polish
- Tolerates rough edges if the core data is accurate and accessible

**Key Metric:** Hours saved per month on market research (target: 8-12 hours/month)

---

## Persona 2: The Real Estate Data Analyst

**Discovery Status:** Hypothesized (adjacent to Persona 1 but distinct role)

**Name:** Morgan — the numbers person

**Profile:**
- Works at a small development firm or consultancy
- Produces market analysis reports for multiple projects simultaneously
- Strong with spreadsheets and data; may know SQL but not necessarily Python
- Evaluates 5-10 potential sites per month across different Seattle neighborhoods
- Needs to compare corridors, not just individual addresses

**Goals:**
- Rapidly screen multiple sites for development potential
- Generate consistent, repeatable market analyses across projects
- Build a data library of corridor activity over time
- Produce deliverables that principals and partners can use in investor or bank conversations

**Pain Points:**
- Currently relies on a patchwork of bookmarked websites, saved spreadsheets, and manual processes
- Each new project requires rebuilding the research from scratch
- No easy way to compare corridors side-by-side
- Spends more time gathering data than analyzing it

**Technical Profile:**
- Comfortable with: Excel, Google Sheets, possibly Tableau or Power BI
- Familiar with: Basic data concepts, pivot tables, formulas
- Not comfortable with: Python, command line, API configuration
- Needs: A lower technical bar than Persona 1; ideally a web interface or pre-built integration

**Relationship to Product:**
- Would use a web dashboard or API more readily than an MCP server
- Values consistency and reliability over flexibility
- Needs export to Excel/CSV for further analysis
- Willing to pay for a tool that saves 10+ hours/week

**Key Metric:** Sites screened per hour (currently ~2, target: ~8-10)

**Validation Questions:**
- Does this person actually exist in the Seattle small-development ecosystem?
- What tools do they currently use? Would they switch?
- What's their budget for data tools?

---

## Persona 3: The Neighborhood Loan Officer

**Discovery Status:** Hypothesized (informed by UC-07)

**Name:** Patricia — the risk assessor

**Profile:**
- Works at a community bank or credit union that does construction lending
- Reviews 3-5 construction loan applications per month
- Needs to assess market context for each application but doesn't have dedicated research staff
- Relies heavily on appraisals but wants supplementary market data
- Not technical; uses bank-provided software and standard office tools

**Goals:**
- Quickly validate that a borrower's market claims are supported by data
- Identify red flags (declining corridor, overvalued comps, permit denials)
- Build confidence in approval recommendations with data-backed context
- Reduce turnaround time on construction loan pre-screening

**Pain Points:**
- Borrower-provided market data is sometimes cherry-picked or outdated
- Independent market research is time-consuming and outside core competency
- Appraisals take 2-4 weeks and cost $500-1,500; a quick pre-screen would help prioritize
- No tool exists specifically for construction loan market context (existing tools are consumer-focused)

**Technical Profile:**
- Comfortable with: Email, Word, Excel, bank software
- Not comfortable with: APIs, Python, Claude Desktop, MCP
- Needs: A web interface, email delivery, or integration with existing bank workflows
- Would not install or configure developer tools

**Relationship to Product:**
- Would consume outputs (reports, summaries) rather than use the tool directly
- Might use a web portal or receive emailed reports
- Values credibility and data sourcing transparency
- Needs disclaimers and caveats (not a substitute for formal appraisal)

**Key Metric:** Pre-screening time per application (currently ~2 hours, target: ~20 minutes)

**Validation Questions:**
- Do community bank loan officers actually do their own market research, or do they rely entirely on appraisals?
- Would they trust data from an automated tool?
- What format would they need outputs in? PDF? Email summary?

---

## Persona 4: The City Planning Enthusiast

**Discovery Status:** Speculative (potential open-source community user)

**Name:** Alex — the curious citizen

**Profile:**
- Lives in Seattle and is interested in neighborhood development
- May be on a community council, neighborhood board, or just personally curious
- Wants to understand what's being built in their area
- Technically comfortable but not a developer
- Uses Claude or ChatGPT for general queries

**Goals:**
- Understand what construction permits have been issued in their neighborhood
- Track large development projects that might affect their property or community
- Access public data without learning government website interfaces

**Pain Points:**
- SDCI's website is functional but not intuitive for casual users
- Hard to get a "big picture" view of development activity in an area
- No alerting for new permits near their address

**Technical Profile:**
- Comfortable with: Consumer apps, web browsers, possibly Claude
- Not comfortable with: APIs, code, terminal
- Needs: The simplest possible interface

**Relationship to Product:**
- Unlikely to pay but could be a community advocate
- Would use a free web tool or chatbot
- Provides validation that the product is useful beyond professional contexts
- Could be an open-source contributor or tester

**Key Metric:** N/A (engagement-based: queries per month)

---

## Persona Prioritization

| Persona | Priority | Validated? | Revenue Potential | Technical Fit |
|---------|----------|-----------|-------------------|---------------|
| Solo Developer-Investor | Primary | Yes | Medium (willing to pay for time savings) | High (MCP native) |
| Data Analyst | Secondary | No | High (professional tool budget) | Medium (needs lower bar) |
| Loan Officer | Tertiary | No | High (institutional buyer) | Low (needs web/email interface) |
| Planning Enthusiast | Future | No | Low (consumer/free) | Low (needs web interface) |

**Recommendation:** Build for Persona 1 first (already validated). Validate Persona 2 through outreach. Design architecture to eventually serve Persona 3, but don't build for them until the product is stable and a distribution channel exists.

---

## Discovery Backlog

Questions to answer through user research before advancing personas from hypothesized to validated:

1. **For Persona 2 (Data Analyst):** Talk to 3 people at small Seattle development firms. Do they have a dedicated research role? What tools do they use? What would they pay for?

2. **For Persona 3 (Loan Officer):** Talk to 2 community bank loan officers. How do they currently assess market context for construction loans? Would they use a data product? In what format?

3. **For all personas:** What's the minimum data accuracy bar? Is "queries live public APIs" sufficient, or do professional users need validated/audited data?
