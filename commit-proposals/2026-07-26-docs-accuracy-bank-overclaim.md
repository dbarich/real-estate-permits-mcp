# Commit Proposal — Correct the "bank validation" overclaim in README & NARRATIVE

**Date:** 2026-07-26
**Proposed by:** Cowork session (agent proposes; human ratifies)
**Status:** READY TO RATIFY (docs-only; commit/push from host terminal)
**Release:** No version change (docs-only; logged under CHANGELOG `[Unreleased]`)
**Directive:** Executes `DOCS-ACCURACY-CORRECTION-DIRECTIVE.md` (2026-07-21)

## Why
The README and NARRATIVE implied the tool had been validated by a bank / used in
a real bank underwriting process. That is not accurate: no bank or lender has
worked with it. It is one developer's best attempt at what a construction lender
would want to evaluate, informally reviewed by a data scientist and an industry
peer, and seeking real lender feedback. A warm contact at an embedded-mortgage
company may read the repo, so the overclaim must be corrected first.

## Proposed commit message
```
docs: correct bank-validation overclaim in README (best-attempt prototype, seeking lender feedback)

The earlier README/NARRATIVE overstated validation. No bank or lender has
evaluated this tool; these claims are tightened proactively to reflect that,
rather than left to be noticed. Validation to date is informal peer review.
```

## Proactive disclosure (decision)
The overclaim has been public on GitHub since the v0.2.1 push, so correcting it
silently could read as hoping no one noticed. Instead, the commit body owns the
correction explicitly, and the same one-line framing is available for outreach
to the embedded-mortgage contact ("tightening the claims to reflect that no
lender has evaluated it yet"). Owning the line reads as integrity to a
lender-adjacent reader.

## Files changed — what and why
| File | Change | Rationale |
|------|--------|-----------|
| `README.md` | Status line: "single-user validated. Built for a real construction loan application." → best-attempt prototype, not bank-validated, informally peer-reviewed | Removes the core overclaim; keeps the honest hedge |
| `README.md` | "Who it's for": "validated against a real bank underwriting process" → "designed to model what a construction-loan underwriting review calls for … not yet evaluated by a bank or lender" | False claim removed |
| `README.md` | Skill bullet: "formatted Word documents for bank submission" → "for a construction-loan package" | Judgment call (beyond the directive's literal list): "bank submission" implies an actual bank relationship |
| `NARRATIVE-OVERVIEW.md` | "The person we've validated this for" → "The person we built this for" | Soften "validated" → "built for" per directive |
| `NARRATIVE-OVERVIEW.md` | "The builder side is proven (it produced an actual bank underwriting document)." → not put in front of a bank; validation is informal peer review | False bank-document claim removed |
| `NARRATIVE-OVERVIEW.md` | Bottom line: "one developer uses for real loan applications" → best-attempt prototype, no bank has evaluated it, that's the validation we're seeking | Removes "real loan applications" implication |
| `CHANGELOG.md` | Added a `### Docs` note under `[Unreleased]` | Version/CHANGELOG discipline, docs-only |

## Alternatives considered
- **Cut a `v0.2.3-alpha` docs patch** vs. log under `[Unreleased]`. Chose
  Unreleased: bumping the version requires editing `__version__` in
  `src/seattle_permits_server.py`, which the directive explicitly forbids
  ("No changes to src/"). Logging under Unreleased honors both the CHANGELOG
  discipline and the no-src rule. Devin can promote it to a numbered release at
  ratification if he'd rather (he'd bump both version sources then).
- **Soften the README skill bullet ("bank submission")** vs. leave it. The
  directive's phrase list didn't include it, but "submission" implies a bank
  actually received the document. Softened for consistency with the directive's
  principle; flagged here since it's a judgment call — revert if you disagree.
- **Edit `NARRATIVE-OVERVIEW.md` at all**, given it is gitignored (see below) —
  vs. skip it. Edited it: the directive explicitly lists it, and it may be shared
  directly or published later. But note it will NOT reach GitHub as-is.

## Spotted but deliberately NOT changed (out of directive scope)
- `README.md` "**No input validation** — bad addresses fail silently" (in
  "What Doesn't Work Yet") is now **stale**: input validation shipped in
  v0.2.0-alpha. This is a separate docs-accuracy issue; flagging for a future
  pass rather than touching it under a bank-overclaim directive.
- `README.md` "3 proven, 4 projected" use-cases link and "real skills used in
  production" — "proven"/"production" refer to the builder's own use, not bank
  validation. Left as-is; raise if you want them softened too.

## Gitignore note (needs your decision)
`NARRATIVE-OVERVIEW.md` is gitignored, so the corrected version will **not** be
committed or pushed — an outside reader on GitHub won't see it either way. The
README is the file that actually reaches your embedded-mortgage contact. If you
want the (now-corrected) narrative to be shareable in the repo, un-ignore it in
`.gitignore`; otherwise it stays local and only the README correction ships.

## Definition of done — verified
- Grep of `README.md` / `NARRATIVE-OVERVIEW.md` for `bank`/`validated`/`real loan`:
  remaining hits either explicitly deny validation or are honest hedges
  (unvalidated lender hypothesis, "What We Don't Know Yet") — none imply bank blessing.
- No changes to `src/`, tools, or tests.

## Ratify steps (host terminal)
```bash
cd ~/Real-Estate-Permits-MCP
./precommit-unlock.sh
git add README.md CHANGELOG.md \
        commit-proposals/2026-07-26-docs-accuracy-bank-overclaim.md
# NARRATIVE-OVERVIEW.md is gitignored — only add it if you first un-ignore it.
git commit -m "docs: correct bank-validation overclaim in README (best-attempt prototype, seeking lender feedback)"
git push origin main
```
