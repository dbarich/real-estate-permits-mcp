# Directive — Correct the "bank validation" overclaim in README & NARRATIVE

**Date:** 2026-07-21
**From:** Devin (via job-hunt Cowork session)
**Scope:** Documentation accuracy only. **No code, no tool behavior changes.**
**Workflow:** Route this through the repo's propose-then-ratify pattern — write a commit
proposal under `commit-proposals/`, then Devin commits/pushes from the host terminal.

---

## Why this matters

The README and NARRATIVE currently imply the tool has been **validated by a bank / used in a
real bank underwriting process**. That is not accurate and needs to be corrected before the repo
is shared with an outside reader (a warm contact at an embedded-mortgage company may read it).

**The truth to represent (Devin's words):**
> No actual banks have worked with me. This product is my **best attempt at what I think a bank
> or construction lender would want to evaluate**. It has been reviewed informally by a data
> scientist (Zillow) and an industry peer — not by any lender.

Principle: the tool is a **builder's best-attempt prototype of a lender-facing underwriting-support
tool**, informally peer-reviewed, and **seeking** real lender feedback — not something a bank has
blessed. Keep every existing hedge; remove every claim of bank validation.

---

## Specific edits

Grep for these phrases (wording may have drifted — search, don't assume line numbers):

| File | Current phrase (remove/soften) | Problem |
|------|-------------------------------|---------|
| `README.md` | "single-user validated. Built for a real construction loan application." | implies a real/bank loan application |
| `README.md` | "validated against a real bank underwriting process" | false — no bank involved |
| `NARRATIVE-OVERVIEW.md` | "The builder side is proven (it produced an actual bank underwriting document)." | false — no bank document |
| `NARRATIVE-OVERVIEW.md` | "one developer uses for real loan applications" | implies submitted loan applications |
| `NARRATIVE-OVERVIEW.md` | "The person we've validated this for is a solo developer-investor" | soften "validated" → "built this for" |

Leave untouched the parts that are **already honestly hedged** — e.g., the lender side described as
an "unvalidated hypothesis," and the "What We Don't Know Yet" section. Those are good and should stay.

---

## Drop-in replacement copy

**README — status line:**
> **Status: alpha** — Working prototype, single-user (builder side). This is one developer's best
> attempt at the market-context and underwriting package a construction lender would want to
> evaluate. It has **not** been validated by any bank or lender; to date it has been reviewed
> informally by a data scientist and an industry peer. Seeking feedback from developers, lenders,
> and real estate professionals in the Seattle market.

**README — "Who it's for" (the validation sentence):**
> The tool was built by one developer and is designed to model what a construction-loan
> underwriting review calls for. It has not yet been evaluated by a bank or lender — that feedback
> is exactly what we're looking for.

**NARRATIVE — "Two Sides" builder-validation sentence:**
> The person we built this for is a solo developer-investor — technically comfortable, working on a
> sub-$1M project, doing their own market research because hiring a consultant doesn't pencil out at
> that scale.

**NARRATIVE — replace the "builder side is proven" passage:**
> Neither side has been validated by a real lender yet. The builder side is the primary use case —
> the tool produces the kind of market-context package a construction-loan application requires —
> but it has **not** been put in front of a bank; validation to date is informal review by a data
> scientist and an industry peer. The lender side is a further hypothesis, based on the observation
> that both parties need the same data for the same transaction but currently pull it independently.

**NARRATIVE — bottom line:**
> Right now this is a working prototype: one developer's best attempt at the underwriting-support
> tool both sides of the construction-lending table would want. No bank has evaluated it yet — that's
> the validation we're seeking.

---

## What NOT to change

- No changes to `src/`, tools, tests, or the 8-tool behavior.
- Don't remove honest hedges or the "What We Don't Know Yet" section — strengthen them if anything.
- Don't add any new claims (e.g., don't name the Zillow reviewer; "a data scientist" is enough).
- Keep the version/CHANGELOG discipline: if this ships as a release, note it as a docs-only patch
  (e.g., `vX.Y.Z-alpha` housekeeping) in `CHANGELOG.md`.

---

## Definition of done

- No occurrence of "bank" implying validation remains in `README.md` or `NARRATIVE-OVERVIEW.md`
  (grep: `bank`, `validated`, `real loan`).
- The docs read as: honest best-attempt prototype, informally peer-reviewed, seeking lender feedback.
- A commit proposal exists under `commit-proposals/` describing the change; Devin ratifies from host.
