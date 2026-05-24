# Real Estate Permits MCP — Product Lifecycle Framework

## Purpose

This document defines the product development lifecycle (PDLC) for the Real Estate Permits MCP server (currently serving Seattle/King County). It adapts a stage-gate methodology to a developer-tools product, providing clear phase definitions, gate criteria, required artifacts, and decision points.

The framework serves three functions: it tells us where we are, what we need to decide next, and what "done" looks like at each stage.

---

## Lifecycle Stages

```
┌──────────┐   ┌───────────┐   ┌──────────┐   ┌──────┐   ┌──────┐   ┌─────────┐   ┌──────────┐   ┌─────────┐
│ NARRATIVE │──▶│ USE CASES │──▶│ PERSONAS │──▶│ ADRs │──▶│ TDDs │──▶│PROTOTYPE│──▶│   BETA   │──▶│ RELEASE │
│           │   │           │   │          │   │      │   │      │   │         │   │          │   │         │
│ Why does  │   │ What do   │   │ Who are  │   │ What │   │ How  │   │ Does it │   │ Does it  │   │ Is it   │
│ this      │   │ people    │   │ they?    │   │ did  │   │ does │   │ work?   │   │ hold up? │   │ ready?  │
│ exist?    │   │ do with   │   │          │   │ we   │   │ it   │   │         │   │          │   │         │
│           │   │ it?       │   │          │   │decide│   │ work?│   │         │   │          │   │         │
└──────────┘   └───────────┘   └──────────┘   └──────┘   └──────┘   └─────────┘   └──────────┘   └─────────┘
```

---

## Stage 1: Narrative

**Question:** Why does this product exist? What problem does it solve? What's the market thesis?

**Artifacts:**
- `01-narrative/NARRATIVE.md` — Problem statement, vision, market context, differentiation thesis

**Gate Criteria (advance when):**
- [ ] Problem statement is specific and falsifiable
- [ ] At least one "who cares?" test has been applied (can you name a real person who would pay/use this?)
- [ ] Market context acknowledges existing alternatives and articulates why they're insufficient
- [ ] Vision statement is bounded (says what the product is NOT as clearly as what it IS)

**Key Decisions:**
- Is this a tool, a platform, or infrastructure?
- Is this Seattle-specific or generalizable?
- Is this for developers, domain experts, or both?

---

## Stage 2: Use Cases

**Question:** What do people actually do with this? What workflows does it enable?

**Artifacts:**
- `02-use-cases/USE_CASES.md` — Concrete scenarios with actors, triggers, steps, and outcomes

**Gate Criteria (advance when):**
- [ ] At least 3 use cases documented from real usage (not hypothetical)
- [ ] At least 2 use cases documented from projected/discovered usage
- [ ] Each use case has a clear trigger, actor, and measurable outcome
- [ ] Use cases are prioritized (must-have vs. nice-to-have)

**Key Decisions:**
- Which use cases define the core product vs. extensions?
- Which use cases are currently served vs. aspirational?

---

## Stage 3: Personas

**Question:** Who are the users? What do they know, what do they need, and what constraints do they operate under?

**Artifacts:**
- `03-personas/PERSONAS.md` — User archetypes with context, goals, pain points, and technical profile

**Gate Criteria (advance when):**
- [ ] At least 2 primary personas defined with real-world grounding
- [ ] Each persona maps to at least one use case
- [ ] Technical sophistication level is specified for each persona
- [ ] At least one persona represents a non-obvious user (discovered through use case analysis)

**Key Decisions:**
- Who is the primary persona (the one we optimize for first)?
- What's the minimum technical bar for using the product?

---

## Stage 4: Architecture Decision Records (ADRs)

**Question:** What did we decide, why, and what were the alternatives?

**Artifacts:**
- `04-adrs/ADR-NNN-title.md` — One file per decision, using standard ADR format

**ADR Format:**
```
# ADR-NNN: [Title]
Status: [Proposed | Accepted | Deprecated | Superseded]
Date: YYYY-MM-DD
Context: What situation prompted this decision?
Decision: What did we decide?
Alternatives Considered: What else was on the table?
Consequences: What follows from this decision?
```

**Gate Criteria (advance when):**
- [ ] All foundational architecture decisions are documented (protocol, data sources, deployment model)
- [ ] No unresolved blocking decisions remain
- [ ] Each ADR links to the use case(s) it serves

**Key Decisions:**
- MCP vs. REST API vs. both?
- Single-city vs. multi-city architecture?
- Real-time vs. cached data strategy?

---

## Stage 5: Technical Design Documents (TDDs)

**Question:** How does the system work? What are the interfaces, data flows, and failure modes?

**Artifacts:**
- `05-tdds/TDD-NNN-title.md` — Technical specifications with diagrams, API contracts, data schemas

**Gate Criteria (advance when):**
- [ ] System architecture is documented with component diagram
- [ ] All external API dependencies are specified with failure handling
- [ ] Data model is defined
- [ ] At least one TDD exists for each core subsystem

**Key Decisions:**
- What's the testing strategy?
- What's the error handling philosophy?
- What's the data freshness guarantee?

---

## Stage 6: Prototype

**Question:** Does it work? Can someone use it to accomplish a real task?

**Artifacts:**
- Working code in `src/`
- At least one integration test in `tests/`
- README with setup instructions

**Gate Criteria (advance when):**
- [ ] At least 2 use cases can be completed end-to-end
- [ ] A non-author has successfully set up and used the tool
- [ ] Known limitations are documented
- [ ] Error handling covers the most common failure modes (API timeout, bad input, no results)

**Current Status: WE ARE HERE.** The existing MCP server is a working prototype. It serves real use cases (bank underwriting research, corridor market analysis) but has not been tested by anyone other than the author.

---

## Stage 7: Beta

**Question:** Does it hold up under real-world use? What breaks? What's missing?

**Artifacts:**
- Beta user feedback log
- Bug/issue tracker
- Performance baseline measurements
- Updated ADRs for any decisions that changed during beta

**Gate Criteria (advance when):**
- [ ] At least 3 beta users have used the tool independently
- [ ] Critical bugs from beta are resolved
- [ ] Performance is acceptable (query response < 10s for 90th percentile)
- [ ] Documentation is sufficient for self-service setup
- [ ] No data accuracy issues reported

**Key Decisions:**
- What's the support model?
- What's the update/release cadence?
- Is packaging needed (pip install, npm, Docker)?

---

## Stage 8: Product Release

**Question:** Is it ready for general availability?

**Artifacts:**
- Release notes
- Published package or distribution
- Landing page or README that serves as product documentation
- License decision

**Gate Criteria (advance when):**
- [ ] All beta gate criteria met
- [ ] Distribution mechanism is in place
- [ ] License is chosen and applied
- [ ] At least one public channel exists for feedback/issues
- [ ] Success metrics are being tracked

---

## Cross-Cutting Concerns

These apply across all stages:

| Concern | Tracked In | Review Cadence |
|---------|-----------|----------------|
| Security (API keys, data exposure) | ADRs | Every stage gate |
| Data accuracy & freshness | TDDs, Metrics | Continuous |
| Legal (data licensing, terms of use) | ADRs | Before beta |
| Accessibility (who can use this) | Personas, TDDs | Before beta |
| Cost (API costs, hosting) | Metrics | Before beta |

---

## How to Use This Framework

1. **Read the current stage's artifacts** to understand where we are
2. **Check the gate criteria** to see what's needed to advance
3. **Write or update artifacts** as you make progress
4. **Record decisions in ADRs** whenever you make a non-trivial choice
5. **Update this document** if the framework itself needs to evolve

The framework is a tool, not a bureaucracy. Skip what doesn't apply. Add what's missing. The goal is traceability from "why" to "how" to "does it work."
