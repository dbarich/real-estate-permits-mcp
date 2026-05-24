# Use Cases: Real Estate Permits MCP

## Use Case Classification

- **Proven**: Derived from actual usage in the Bookstorhaus project
- **Projected**: Derived from analysis of adjacent workflows that the tool could serve
- **Speculative**: Hypothesized based on market gaps; requires validation

---

## UC-01: Bank Underwriting Market Analysis (Proven)

**Priority:** Must-have (this is the use case that created the product)

**Actor:** Small-scale developer preparing a construction loan application

**Trigger:** Developer needs to demonstrate market context for a bank underwriter — comparable project values, development activity in the corridor, property appreciation trends.

**Preconditions:**
- Developer has a target property address
- Developer has Claude Desktop with the MCP server configured
- Developer knows the ZIP codes and street corridors relevant to their project

**Steps:**
1. Developer asks Claude to pull development comparables for their target address
2. MCP server queries Seattle SDCI for permit activity on the corridor (multiple street names)
3. MCP server queries King County Assessor for parcel sales data near the target
4. Claude synthesizes the data into a narrative: X permits issued, $Y total development value, Z comparable sales at $W/sqft
5. Developer (or a skill) generates a formatted Word document for bank submission

**Outcome:** A dated, professional market analysis document with current data, suitable for inclusion in a construction loan package.

**Measurable Success:** Document accepted by bank underwriter as sufficient market context (has happened — this use case is validated).

**Current Gaps:**
- No automated diff against previous pulls (the skill handles this, but it's fragile)
- No confidence scoring on comparables (are these really comparable, or just nearby?)
- No visualization (maps, charts) in the output

---

## UC-02: Ad-Hoc Corridor Research (Proven)

**Priority:** Must-have

**Actor:** Developer or investor evaluating a potential acquisition or development site

**Trigger:** "What's happening on [street name]?" — the developer wants a quick read on permit activity, property values, and development momentum in a specific corridor.

**Steps:**
1. Developer asks Claude about a street or ZIP code
2. MCP server pulls permit data filtered by location and timeframe
3. MCP server pulls parcel sales data for the same area
4. Claude presents a structured summary: recent permits, high-value projects, comparable lot sales

**Outcome:** A conversational summary of development activity that would otherwise require 30-60 minutes of manual research across multiple websites.

**Measurable Success:** Developer makes an informed go/no-go decision on a site within one conversation.

---

## UC-03: Permit Tracking Over Time (Proven)

**Priority:** Should-have

**Actor:** Developer monitoring a corridor for changes during a multi-month project timeline

**Trigger:** Bi-weekly schedule (or on-demand) to check for new permits, status changes, and new property sales in the project area.

**Steps:**
1. Skill triggers on schedule (or developer requests a market pull)
2. MCP server pulls current permit and parcel data
3. Skill loads previous snapshot from `market_snapshots/` directory
4. Skill diffs current vs. previous: new permits, status changes, price movements
5. Skill generates a Word document with a "Changes Since Last Report" section
6. Snapshot is saved for next comparison

**Outcome:** A running timeline of market data that the bank can review, demonstrating ongoing monitoring and market consistency.

**Current Gaps:**
- Snapshot diffing is implemented in the skill but not in the MCP server itself
- No alerting mechanism (you have to remember to run it or wait for the schedule)
- Snapshots are local JSON files with no schema validation

---

## UC-04: Comparable Project Discovery (Projected)

**Priority:** Should-have

**Actor:** Developer or appraiser looking for truly comparable projects — not just nearby parcels, but projects with similar scope (unit count, building type, lot size, construction cost).

**Trigger:** "Find me projects similar to mine" — the user needs comps that match on multiple dimensions, not just geography.

**Steps:**
1. User describes their project: 3-unit stacked flat, 1,668 sqft lot, ~$650K construction cost, LR1(M) zone
2. MCP server searches permits by description keywords (MULTI, DUPLEX, TRIPLEX, STACKED)
3. MCP server cross-references with parcel data for lot size and zoning
4. Results are filtered and ranked by similarity to the user's project
5. Claude presents the top matches with a relevance explanation

**Outcome:** A shortlist of genuinely comparable projects with permit details and property context, suitable for appraisal support or bank underwriting.

**What's Missing Today:**
- No similarity scoring or multi-dimensional filtering
- No cross-reference between permit descriptions and parcel attributes
- `get_multifamily_permits` uses keyword matching but doesn't score relevance

---

## UC-05: Zoning Feasibility Check (Projected)

**Priority:** Could-have

**Actor:** Developer evaluating whether a site can support their intended project before engaging an architect or planner.

**Trigger:** "Can I build [project type] on [address]?" — the user wants a quick feasibility read before investing in professional services.

**Steps:**
1. User provides an address and intended project type
2. MCP server pulls parcel data including zoning code
3. MCP server pulls recent permits at the same address and nearby (to see what's been approved)
4. Claude interprets the zoning code against the project type and presents a preliminary assessment
5. Claude caveats that this is informational, not legal advice, and recommends SDCI confirmation

**Outcome:** A preliminary feasibility assessment that saves the developer from pursuing obviously infeasible sites.

**What's Missing Today:**
- No zoning code interpretation logic (the MCP returns raw zone codes like "LR1(M)" but doesn't explain what's allowed)
- No FAR/height/setback calculations
- Would need Seattle Municipal Code data or a mapping table

---

## UC-06: Real Estate Agent Site Evaluation (Speculative)

**Priority:** Could-have (depends on persona validation)

**Actor:** Real estate agent representing a buyer interested in development potential, or a listing agent positioning a lot for developers.

**Trigger:** Agent needs to quickly assess development potential and recent activity for a property they're showing or listing.

**Steps:**
1. Agent provides a property address
2. MCP server pulls parcel details, permit history, and nearby development activity
3. Claude produces a development potential summary: zoning, recent comparables, active permits in corridor
4. Agent uses this to inform their client or listing description

**Outcome:** A data-backed development potential summary that the agent can share with clients.

**Validation Needed:** Do agents actually want this? What format do they need it in? Would they use Claude Desktop, or does this need a different interface?

---

## UC-07: Loan Officer Pre-Screening (Speculative)

**Priority:** Could-have (depends on persona validation)

**Actor:** Bank loan officer or underwriter doing preliminary assessment of a construction loan application.

**Trigger:** Application arrives for a construction loan; officer needs to quickly assess whether the market context supports the project.

**Steps:**
1. Loan officer provides the project address
2. MCP server pulls permit activity, parcel comparables, and development context
3. Claude generates a market context summary focused on underwriting concerns: comparable valuations, development momentum, risk factors
4. Officer uses this to inform their initial assessment

**Outcome:** Faster pre-screening of construction loan applications with data-backed market context.

**Validation Needed:** Would loan officers use an MCP tool? Do they have Claude Desktop? This may need to be a web interface or API integration with their existing systems.

---

## Use Case Priority Matrix

| ID | Use Case | Priority | Status | Primary Persona |
|----|----------|----------|--------|-----------------|
| UC-01 | Bank Underwriting Analysis | Must-have | Proven | Solo Developer |
| UC-02 | Ad-Hoc Corridor Research | Must-have | Proven | Solo Developer |
| UC-03 | Permit Tracking Over Time | Should-have | Proven | Solo Developer |
| UC-04 | Comparable Project Discovery | Should-have | Projected | Solo Developer, Appraiser |
| UC-05 | Zoning Feasibility Check | Could-have | Projected | Solo Developer, Agent |
| UC-06 | Agent Site Evaluation | Could-have | Speculative | Real Estate Agent |
| UC-07 | Loan Officer Pre-Screening | Could-have | Speculative | Loan Officer |
