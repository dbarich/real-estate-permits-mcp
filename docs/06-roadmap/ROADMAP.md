# Product Roadmap: Real Estate Permits MCP

## Current Position

**Stage: Prototype → Hardening (Fork A selected May 24, 2026)**

The MCP server runs, serves real data, and has been used to produce actual bank underwriting documents. Repo is live on GitHub (github.com/dbarich/real-estate-permits-mcp), tagged v0.1.0-alpha. Two testers recruited: an engineer reviewing code, and a Zillow data scientist (Bryson) reviewing use case/usability. Devin is shifting primary focus to the FIDIC Tool project; this project is on a minimal-effort path to a testable skeleton.

**Development Fork:** Fork A — MCP Hardening (stay in Claude Desktop, no new UI). Fix bugs, add validation, let testers use it as-is. Tests the hypothesis that the Claude natural language interface is the product, not just a wrapper.

**Alternatives considered and deferred:**
- Fork B (Streamlit thin client): Revisit if feedback indicates non-technical users need a GUI
- Fork C (Static showcase + recorded demos): May layer on after Bryson demo is recorded

---

## Phase 1: Prototype Hardening (Active — target: June 7, 2026)

**Goal:** Make the existing tool reliable and testable enough to hand to someone else. Minimal effort — fix what's broken, validate with 2 testers, learn.

**Deliverables:**

- [x] README with setup instructions clear enough for a non-author to follow
- [x] Published to GitHub as public repository
- [x] Demo script with real query sequences for advisor conversation
- [x] Fix parcel address lookup bug — Layer 2 (Parcels) as primary, address-format permutations, debug logging (May 24, 2026)
- [x] Input validation on parcel-lookup tools (empty/malformed address handling) — partial; rest of tools pending
- [ ] Error type differentiation (no results vs. API error vs. timeout)
- [x] Basic smoke tests for parcel lookup (tests/test_parcel_lookup.py covers 3 target addresses + validation)
- [ ] Socrata app token support (environment variable, optional)

**Deferred from original plan (revisit post-feedback):**
- Structured JSON output mode — only build if testers request it
- Comprehensive test suite — smoke tests are sufficient for alpha

**Gate:** Both testers can install, configure, and successfully run 3 use cases without author assistance.

**Risk:** Dependency on FastMCP stability — if the MCP SDK changes, the server needs updating.

---

## Phase 2: Beta (Target: late June 2026)

**Goal:** Get 3-5 real users running the tool and providing feedback. Keep scope small — this is a side project.

**Deliverables (already done):**

- [x] Published to GitHub as a public repository
- [x] 2 example skills bundled (dearborn-mcp + dearborn-market-pull)
- [x] Feedback mechanism (GitHub Issues)
- [x] Comprehensive README with setup instructions

**Deliverables (remaining):**

- [ ] pip-installable package (or at minimum, clear dependency management)
- [ ] Claude Desktop MCP config template (copy-paste setup)
- [ ] Decide: Streamlit thin client (Fork B) based on Phase 1 feedback

**User Recruitment Strategy:**
- Engineer tester (recruited, reviewing code)
- Bryson / Zillow data scientist (recruited, reviewing use case)
- Post in Anthropic MCP community (Discord, GitHub discussions)
- 1-2 additional Seattle real estate developers if initial feedback is positive

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

## Timeline (Updated May 24, 2026)

```
May 2026                    Jun 2026                    Jul 2026
    │                           │                           │
    ├─ v0.1.0-alpha (DONE) ─┐   │                           │
    │  GitHub live, 2 testers│   │                           │
    │                       ├── Hardening (Fork A) ──┐      │
    │                           │  Bug fix, validation│      │
    │                           │  Target: Jun 7      │      │
    │                           │                     ├── Beta
    │                           │                     │  Target: late Jun
    │                           │                     │
    │                           │                     │  V1 / Expansion: TBD
    │                           │                     │  based on feedback
```

These timelines assume LOW effort — Devin's primary focus is on the FIDIC Tool project. This project is in maintenance/validation mode: fix what's broken, collect feedback, decide whether to invest further based on tester signal.
