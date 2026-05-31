# Product Roadmap: Real Estate Permits MCP

## Current Position

**Stage: Hardening (Fork A) — Phase 1 technical work complete, awaiting tester feedback (May 31, 2026)**

The MCP server runs, serves real data, and has been used to produce actual bank underwriting documents. Repo is live on GitHub (github.com/dbarich/real-estate-permits-mcp), tagged **v0.2.0-alpha** (May 28, 2026). All eight tools are hardened with input validation, SoQL sanitization, and three-tier error differentiation; integration tests pass 14/14. The only remaining Phase 1 item is the human gate: both testers running 3 use cases without author assistance. Two testers recruited: an engineer reviewing code (URL shared), and a Zillow data scientist (Bryson) reviewing use case/usability (onboarding package ready, no date scheduled). Devin is shifting primary focus to the FIDIC Tool project; this project is now in validation mode pending tester signal.

**Development Fork:** Fork A — MCP Hardening (stay in Claude Desktop, no new UI). Fix bugs, add validation, let testers use it as-is. Tests the hypothesis that the Claude natural language interface is the product, not just a wrapper.

**Alternatives considered and deferred:**
- Fork B (Streamlit thin client): Revisit if feedback indicates non-technical users need a GUI
- Fork C (Static showcase + recorded demos): May layer on after Bryson demo is recorded

---

## Phase 1: Prototype Hardening (Technical work complete — gate open, target: June 7, 2026)

**Goal:** Make the existing tool reliable and testable enough to hand to someone else. Minimal effort — fix what's broken, validate with 2 testers, learn.

**Deliverables:**

- [x] README with setup instructions clear enough for a non-author to follow
- [x] Published to GitHub as public repository
- [x] Demo script with real query sequences for advisor conversation
- [x] Fix parcel address lookup bug — Layer 2 (Parcels) as primary, address-format permutations, debug logging (v0.1.1-alpha, May 24, 2026)
- [x] Input validation on **all 8 tools** — ZIP/PIN/permit regex, street-name minimums, days_back/limit bounds clamping (v0.2.0-alpha, May 28, 2026)
- [x] Error type differentiation across all tools (no results vs. API error vs. timeout) with actionable messages (v0.2.0-alpha)
- [x] SoQL sanitization — `_sanitize_soql()` escapes user input before WHERE-clause interpolation (v0.2.0-alpha)
- [x] Socrata app token support (optional `SOCRATA_APP_TOKEN` env var, prevents rate limiting) (v0.2.0-alpha)
- [x] NoneType null-field bug fix in `get_parcel_by_pin` (`(value or 'N/A')` pattern) (v0.2.0-alpha)
- [x] Smoke tests for parcel lookup (tests/test_parcel_lookup.py — 3 addresses, PIN, 10 validation cases, no-results path, sanitization)
- [x] Integration test across 2 properties + validation probes (tests/integration_test.py) — 14/14 passing
- [x] Quick-start onboarding — `setup.sh` auto-installer + `QUICKSTART.md` with evaluation questions
- [ ] **Gate (open): Both testers install, configure, and successfully run 3 use cases without author assistance**

**Deferred from original plan (revisit post-feedback):**
- Structured JSON output mode — only build if testers request it
- Comprehensive test suite — smoke + integration tests are sufficient for alpha

**Risk:** Dependency on FastMCP stability — if the MCP SDK changes, the server needs updating. Validation risk now dominant: progress is gated entirely on two human testers responding.

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
- [x] Changelog and versioning (semver) — CHANGELOG.md added, version synced across pyproject + server (`__version__`)

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

## Timeline (Updated May 31, 2026)

```
May 2026                        Jun 2026                    Jul 2026
    │                               │                           │
    ├─ v0.1.0-alpha (DONE) ─┐       │                           │
    ├─ v0.1.1-alpha (DONE) ─┤       │                           │
    │  parcel lookup fix     │       │                           │
    ├─ v0.2.0-alpha (DONE) ──┤       │                           │
    │  validation, sanitize, │       │                           │
    │  errors, tests 14/14   │       │                           │
    │                        └── Hardening gate ──┐             │
    │                            (awaiting tester  │             │
    │                             feedback)        │             │
    │                            Target: Jun 7     ├── Beta      │
    │                                              │  Target: late Jun
    │                                              │             │
    │                                              │  V1 / Expansion: TBD
    │                                              │  based on feedback
```

All v0.2.0-alpha technical hardening is complete. The Phase 1 gate is now the bottleneck — it depends entirely on two human testers, not further engineering. These timelines assume LOW effort: Devin's primary focus is the FIDIC Tool project. This project is in validation mode — collect tester signal, then decide whether to invest further.
