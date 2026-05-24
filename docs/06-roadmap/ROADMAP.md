# Product Roadmap: Real Estate Permits MCP

## Current Position

**Stage: Prototype (working, single-user, validated for 3 use cases)**

The MCP server runs, serves real data, and has been used to produce actual bank underwriting documents. It has not been tested by anyone other than the author.

---

## Phase 1: Prototype Hardening (Current → 4 weeks)

**Goal:** Make the existing tool reliable and testable enough to hand to someone else.

**Deliverables:**

- [ ] Input validation and address normalization on all tools
- [ ] Error type differentiation (no results vs. API error vs. timeout)
- [ ] Structured JSON output mode (in addition to text) for programmatic consumption
- [ ] Basic test suite: unit tests for query builders, integration tests against live APIs
- [ ] README with setup instructions clear enough for a non-author to follow
- [ ] Socrata app token support (environment variable, optional)

**Gate:** A second person can install, configure, and successfully run 3 use cases without author assistance.

**Risk:** Dependency on FastMCP stability — if the MCP SDK changes, the server needs updating.

---

## Phase 2: Beta (Prototype Gate + 6 weeks)

**Goal:** Get 3-5 real users running the tool and providing feedback.

**Deliverables:**

- [ ] Published to GitHub as a public repository
- [ ] pip-installable package (or at minimum, clear dependency management)
- [ ] Claude Desktop MCP config template (copy-paste setup)
- [ ] 2 example skills bundled (research tool + market pull template)
- [ ] Feedback mechanism (GitHub Issues, or a simple form)
- [ ] Basic documentation site or comprehensive README

**User Recruitment Strategy:**
- Post in Seattle real estate development communities (BiggerPockets Seattle forum, local REIA)
- Share with Anthropic MCP community (Discord, GitHub discussions)
- Direct outreach to 2-3 people who fit Persona 1 or Persona 2

**Gate:** 3+ users have completed at least 1 use case independently and provided feedback.

**Metrics to Track During Beta:**
- Setup success rate (% of attempted installs that result in a working tool)
- Query success rate (% of tool calls that return useful data)
- Time-to-first-value (minutes from install to first useful query)
- Feature requests and pain points (qualitative)

---

## Phase 3: V1 Release (Beta Gate + 4 weeks)

**Goal:** A stable, documented, distributable product that someone can find, install, and use.

**Deliverables:**

- [ ] Stable API surface (tool names and parameters won't change without deprecation)
- [ ] Published package on PyPI or npm (depending on distribution decision)
- [ ] MCP server registry listing (if Anthropic establishes one)
- [ ] Landing page or README that serves as product documentation
- [ ] License chosen and applied (likely MIT or Apache 2.0 for open-source)
- [ ] Changelog and versioning (semver)

**Gate:** Someone you've never met can find, install, and use the tool based solely on public documentation.

---

## Phase 4: Expansion (Post-V1, timeline TBD)

**Goal:** Broaden the product based on validated demand signals from Beta and V1.

**Potential Tracks (choose based on evidence):**

### Track A: Deeper Seattle
- Add land use permit data (dataset `kkzf-ntnu` — already configured but not exposed)
- Add zoning interpretation logic (map zone codes to allowed uses)
- Add historical trend analysis (permit volume over time, price/sqft trends)
- Add SDCI project tracking (link permits to inspections and certificate of occupancy)

### Track B: Multi-City
- Abstract the data source layer to support pluggable city adapters
- Add a second city with strong open data (Portland, Austin, Denver are candidates)
- Define a "city adapter" interface that community contributors could implement

### Track C: Non-MCP Interfaces
- REST API wrapper for web/mobile access
- Simple web dashboard for Persona 2 and 3
- Email/webhook alerts for permit tracking (UC-03)
- Slack integration for team notifications

### Track D: Monetization
- Free tier: basic permit search, limited queries/day
- Pro tier: development comparables, historical tracking, document generation
- Enterprise: custom corridors, API access, bulk export

**Decision Framework:** Choose the track that has the strongest demand signal from Beta users. Don't build Track B or C until Track A is solid.

---

## Decision Points

| Decision | When | Inputs Needed |
|----------|------|---------------|
| Open source vs. proprietary? | Before Beta | Business model hypothesis, competitive landscape |
| License type? | Before Beta | Community strategy, potential enterprise use |
| Multi-city architecture investment? | Post-V1 | Beta feedback, demand signals from other cities |
| Web interface investment? | Post-V1 | Persona 2/3 validation, willingness to pay |
| Pricing model? | Post-V1 | Usage data, competitor pricing, cost of serving |

---

## Timeline (Estimated)

```
Mar 2026          Apr 2026          May 2026          Jun 2026
    │                 │                 │                 │
    ├─ Prototype ─────┤                 │                 │
    │  Hardening      │                 │                 │
    │                 ├─── Beta ────────┤                 │
    │                 │                 │                 │
    │                 │                 ├── V1 Release ───┤
    │                 │                 │                 │
    │                 │                 │                 ├── Expansion ──▶
```

These timelines assume part-time effort (this is a side project alongside the Bookstorhaus development). Adjust if circumstances change.
