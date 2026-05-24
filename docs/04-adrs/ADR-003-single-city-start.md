# ADR-003: Start with Seattle Only, Design for Multi-City Later

**Status:** Proposed
**Date:** 2026-03-07

## Context

The tool currently serves Seattle/King County exclusively. The underlying problem (fragmented municipal data for small-scale developers) exists in every US city with open data portals. The question is whether to architect for multi-city support now or stay focused on Seattle.

## Decision

**Proposed:** Stay Seattle-only for Prototype and Beta stages. Design the code to be refactorable for multi-city support but don't abstract prematurely.

## Alternatives Considered

| Alternative | Pros | Cons |
|------------|------|------|
| Multi-city from day one | Larger addressable market, forces clean abstractions | Slower development, harder to test, each city's data is different |
| Seattle forever | Simpler, deeper, can be the best Seattle tool | Limited market, single point of failure if Seattle changes APIs |
| City-plugin architecture | Extensible, community-contributed | Over-engineering at this stage, no community yet |

## Reasoning

Every city's open data is different — different APIs, different field names, different datasets available. Abstracting over that prematurely would slow down development and produce a worse Seattle experience without validated demand from other cities.

The better path: build the best possible Seattle tool, validate the product-market fit, then use that success to justify the engineering investment in multi-city abstraction.

## Consequences

**Positive:**
- Faster iteration on features that matter to validated users
- Can go deep on Seattle data (add land use permits, zoning interpretation, historical trends)
- Simpler codebase, fewer abstractions

**Negative:**
- Marketing messaging must be Seattle-specific
- Any user outside Seattle/King County gets no value
- If multi-city is eventually needed, some refactoring will be required

## Revisit Trigger

Revisit when: (a) 3+ people from other cities express interest, (b) a second city with comparable open data is identified as a target market, or (c) the product reaches Beta and the next growth lever is geographic expansion.
